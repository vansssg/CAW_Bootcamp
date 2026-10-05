"""Agent 3 — audit log. Consumes activity bus events. No email in metadata."""

from __future__ import annotations

from datetime import datetime, timezone

from app.activity import add_global_listener

entries: list[dict] = []
_next_id = 1
_listening = False


def reset_for_tests() -> None:
    global _next_id
    entries.clear()
    _next_id = 1
    ensure_listening()


def ensure_listening() -> None:
    global _listening
    if not _listening:
        add_global_listener(on_bus_event)
        _listening = True


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def record(
    *,
    action: str,
    resource_type: str,
    resource_id: int | str,
    actor_id: str,
    metadata: dict | None = None,
    team_id: int | None = None,
) -> dict:
    global _next_id
    meta = dict(metadata or {})
    meta.pop("email", None)
    row = {
        "id": _next_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "actor_id": actor_id,
        "metadata": meta,
        "team_id": team_id,
        "ts": _now(),
    }
    _next_id += 1
    entries.append(row)
    return row


def on_bus_event(event: dict) -> None:
    event_type = str(event.get("type") or "")
    payload = dict(event.get("payload") or {})
    payload.pop("email", None)
    team_id = event.get("team_id")
    if event_type == "invitation.accepted":
        record(
            action="accepted",
            resource_type="invitation",
            resource_id=payload.get("invitation_id") or 0,
            actor_id=str(payload.get("accepted_by") or ""),
            metadata=payload,
            team_id=team_id,
        )
        return
    if event_type == "mention.notified":
        record(
            action="notify",
            resource_type="mention",
            resource_id=payload.get("source_id") or 0,
            actor_id=str(payload.get("mentioned_principal") or ""),
            metadata=payload,
            team_id=team_id,
        )
        return
    if "." not in event_type:
        return
    resource_type, action = event_type.split(".", 1)
    if action not in {"created", "updated", "deleted"}:
        return
    resource_id = (
        payload.get("comment_id")
        or payload.get("invitation_id")
        or payload.get("id")
        or 0
    )
    actor_id = str(payload.get("author_id") or payload.get("invited_by") or payload.get("accepted_by") or "")
    record(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor_id,
        metadata=payload,
        team_id=team_id,
    )


def list_for_team(team_id: int) -> list[dict]:
    return [row for row in entries if row.get("team_id") == int(team_id)]


ensure_listening()
