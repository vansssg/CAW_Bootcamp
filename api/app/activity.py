"""Team activity feed: service-layer pub/sub. Memory-backed; not Postgres NOTIFY."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Callable

from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from app.auth import API_KEYS

HEARTBEAT_INTERVAL_S = 30
HEARTBEAT_PONG_TIMEOUT_S = 10
MAX_EVENTS_PER_TEAM = 200

EventHandler = Callable[[dict], None]

_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=MAX_EVENTS_PER_TEAM))
_subscribers: dict[int, list[EventHandler]] = defaultdict(list)
_global_listeners: list[EventHandler] = []


def reset_for_tests() -> None:
    _history.clear()
    _subscribers.clear()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def publish(team_id: int, event_type: str, payload: dict | None = None) -> dict:
    event = {
        "type": event_type,
        "team_id": int(team_id),
        "ts": _now_iso(),
        "payload": payload or {},
    }
    _history[int(team_id)].append(event)
    for handler in list(_subscribers.get(int(team_id), [])):
        handler(event)
    for handler in list(_global_listeners):
        handler(event)
    return event


def add_global_listener(handler: EventHandler) -> None:
    if handler not in _global_listeners:
        _global_listeners.append(handler)


def global_listener_count() -> int:
    return len(_global_listeners)


def replay_since(team_id: int, since_ts: str | None) -> list[dict]:
    rows = list(_history[int(team_id)])
    if not since_ts:
        return rows
    return [row for row in rows if row["ts"] > since_ts]


def subscribe(team_id: int, handler: EventHandler) -> None:
    _subscribers[int(team_id)].append(handler)


def unsubscribe(team_id: int, handler: EventHandler) -> None:
    bucket = _subscribers.get(int(team_id), [])
    _subscribers[int(team_id)] = [item for item in bucket if item is not handler]


def principal_from_headers(headers: dict[str, str]) -> str:
    key = (headers.get("x-api-key") or "").strip()
    principal = API_KEYS.get(key)
    if principal is None:
        raise HTTPException(status_code=401, detail="API key required")
    return principal


async def activity_socket(websocket: WebSocket, team_id: int, *, require_member) -> None:
    header_map = {
        k.decode("latin-1").lower(): v.decode("latin-1")
        for k, v in websocket.scope.get("headers", [])
    }
    try:
        principal_id = principal_from_headers(header_map)
        require_member(int(team_id), principal_id)
    except HTTPException as exc:
        await websocket.close(code=4401 if exc.status_code == 401 else 4403)
        return
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()

    def _on_event(event: dict) -> None:
        queue.put_nowait(event)

    subscribe(int(team_id), _on_event)
    query = websocket.scope.get("query_string", b"").decode("latin-1")
    since = ""
    for part in query.split("&"):
        if part.startswith("since="):
            since = part.split("=", 1)[1]
    try:
        for event in replay_since(int(team_id), since or None):
            await websocket.send_json(event)

        async def reader():
            while True:
                message = await websocket.receive_json()
                kind = message.get("type") if isinstance(message, dict) else None
                if kind == "ping":
                    await websocket.send_json({"type": "pong", "ts": _now_iso()})

        async def writer():
            while True:
                event = await queue.get()
                await websocket.send_json(event)

        await asyncio.gather(reader(), writer())
    except WebSocketDisconnect:
        pass
    finally:
        unsubscribe(int(team_id), _on_event)
