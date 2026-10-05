"""Agent 1 — team comment threads. Memory-backed; membership via invitations."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException

from app.activity import publish
from app.invitations import require_team_member, require_commenter

comments: dict[int, dict] = {}
_next_id = 1
MAX_BODY = 5000


def reset_for_tests() -> None:
    global _next_id
    comments.clear()
    _next_id = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_comment(team_id: int, principal_id: str, body: str, parent_id: int | None = None) -> dict:
    require_commenter(int(team_id), principal_id)
    text = (body or "").strip()
    if not text or len(text) > MAX_BODY:
        raise HTTPException(status_code=400, detail="Comment body must be 1-5000 characters")
    if parent_id is not None:
        parent = comments.get(int(parent_id))
        if parent is None or parent["team_id"] != int(team_id):
            raise HTTPException(status_code=404, detail="Parent comment not found")
    global _next_id
    comment_id = _next_id
    _next_id += 1
    row = {
        "id": comment_id,
        "team_id": int(team_id),
        "author_id": principal_id,
        "body": text,
        "parent_id": parent_id,
        "created_at": _now(),
    }
    comments[comment_id] = row
    publish(
        int(team_id),
        "comment.created",
        {"comment_id": comment_id, "team_id": int(team_id), "author_id": principal_id},
    )
    from app.mentions import notify, parse

    notify(
        parse(text),
        team_id=int(team_id),
        source_type="comment",
        source_id=comment_id,
        actor_id=principal_id,
    )
    return row


def list_comments(team_id: int, principal_id: str) -> list[dict]:
    require_team_member(int(team_id), principal_id)
    return [row for row in comments.values() if row["team_id"] == int(team_id)]


def update_comment(team_id: int, comment_id: int, principal_id: str, body: str) -> dict:
    require_team_member(int(team_id), principal_id)
    row = comments.get(int(comment_id))
    if row is None or row["team_id"] != int(team_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    if row["author_id"] != principal_id:
        raise HTTPException(status_code=403, detail="You are not allowed to modify this comment.")
    text = (body or "").strip()
    if not text or len(text) > MAX_BODY:
        raise HTTPException(status_code=400, detail="Comment body must be 1-5000 characters")
    row["body"] = text
    publish(
        int(team_id),
        "comment.updated",
        {"comment_id": int(comment_id), "team_id": int(team_id), "author_id": principal_id},
    )
    return row


def delete_comment(team_id: int, comment_id: int, principal_id: str) -> dict:
    require_team_member(int(team_id), principal_id)
    row = comments.get(int(comment_id))
    if row is None or row["team_id"] != int(team_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    if row["author_id"] != principal_id:
        raise HTTPException(status_code=403, detail="You are not allowed to modify this comment.")
    comments.pop(int(comment_id))
    publish(
        int(team_id),
        "comment.deleted",
        {"comment_id": int(comment_id), "team_id": int(team_id), "author_id": principal_id},
    )
    return {"deleted": True, "id": int(comment_id)}
