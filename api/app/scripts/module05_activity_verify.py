"""ASGI WebSocket checks for the activity feed. No httpx."""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.activity import publish, reset_for_tests as reset_activity, _subscribers
from app.auth import API_KEY_A, API_KEY_B
from app.invitations import reset_for_tests
from app.main import app
from app.scripts.module09_test_suite import call


async def ws_exchange(path, headers, incoming, drain_after=0.05):
    sent = []
    incoming = list(incoming)
    done = asyncio.Event()

    async def receive():
        if incoming:
            return incoming.pop(0)
        await done.wait()
        return {"type": "websocket.disconnect", "code": 1000}

    async def send(message):
        sent.append(message)

    header_list = [
        (k.lower().encode("latin-1"), str(v).encode("latin-1")) for k, v in headers.items()
    ]
    q = b""
    if "?" in path:
        path, qs = path.split("?", 1)
        q = qs.encode("latin-1")
    scope = {
        "type": "websocket",
        "asgi": {"spec_version": "2.3", "version": "3.0"},
        "http_version": "1.1",
        "scheme": "ws",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": q,
        "headers": header_list,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "subprotocols": [],
        "state": {},
        "extensions": {},
    }
    task = asyncio.create_task(app(scope, receive, send))
    await asyncio.sleep(drain_after)
    return sent, task, done


def _texts(sent):
    out = []
    for message in sent:
        if message.get("type") == "websocket.send" and "text" in message:
            out.append(json.loads(message["text"]))
        elif message.get("type") == "websocket.close":
            out.append({"close": message.get("code")})
        elif message.get("type") == "websocket.accept":
            out.append({"accept": True})
    return out


async def main_async():
    reset_for_tests()
    reset_activity()
    sent, task, done = await ws_exchange(
        "/ws/teams/1/activity",
        {"X-API-Key": API_KEY_A},
        [{"type": "websocket.connect"}],
    )
    done.set()
    await asyncio.sleep(0.05)
    task.cancel()
    print("VERIFY_WS_ACCEPT", any(m.get("type") == "websocket.accept" for m in sent))

    reset_for_tests()
    reset_activity()
    sent_b, task_b, done_b = await ws_exchange(
        "/ws/teams/1/activity",
        {"X-API-Key": API_KEY_B},
        [{"type": "websocket.connect"}],
        drain_after=0.05,
    )
    publish(1, "invitation.created", {"invitation_id": 99})
    await asyncio.sleep(0.05)
    texts = _texts(sent_b)
    print("VERIFY_WS_EVENT_TYPES", [row.get("type") for row in texts if "type" in row])
    print("VERIFY_WS_GOT_INVITE_EVENT", any(row.get("type") == "invitation.created" for row in texts))
    done_b.set()
    await asyncio.sleep(0.05)
    task_b.cancel()
    print("VERIFY_SUBSCRIBER_CLEANUP", len(_subscribers.get(1, [])) == 0)

    reset_for_tests()
    reset_activity()
    first = publish(1, "invitation.created", {"invitation_id": 1})
    publish(1, "invitation.created", {"invitation_id": 2})
    sent_r, task_r, done_r = await ws_exchange(
        f"/ws/teams/1/activity?since={first['ts']}",
        {"X-API-Key": API_KEY_A},
        [{"type": "websocket.connect"}],
    )
    await asyncio.sleep(0.05)
    replayed = [row for row in _texts(sent_r) if row.get("type") == "invitation.created"]
    ids = [row.get("payload", {}).get("invitation_id") for row in replayed]
    print("VERIFY_RECONNECT_REPLAY_COUNT", len(replayed))
    print("VERIFY_RECONNECT_IDS", ids)
    print("VERIFY_RECONNECT_GOT_MISSED", 2 in ids and 1 not in ids)
    done_r.set()
    task_r.cancel()

    sent_unauth, task_u, done_u = await ws_exchange(
        "/ws/teams/1/activity",
        {},
        [{"type": "websocket.connect"}],
    )
    print("VERIFY_WS_UNAUTH_CLOSE", any(m.get("code") == 4401 for m in sent_unauth))
    done_u.set()
    task_u.cancel()
    await asyncio.sleep(0.05)
    print("VERIFY_HTTP_INVITE", "skipped_nested_asyncio")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
