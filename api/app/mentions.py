"""Agent 2 — mention parser. Does not import comments. No email in events."""

from __future__ import annotations

import re

from app.activity import publish
from app.invitations import PRINCIPAL_EMAIL

MENTION_RE = re.compile(r"@([A-Za-z0-9._-]+)")


def parse(text: str) -> list[dict]:
    found = []
    for match in MENTION_RE.finditer(text or ""):
        username = match.group(1)
        principal_id = username if username in PRINCIPAL_EMAIL else None
        found.append(
            {
                "raw": match.group(0),
                "username": username,
                "principal_id": principal_id,
                "start": match.start(),
                "end": match.end(),
            }
        )
    return found


def notify(mentions: list[dict], *, team_id: int, source_type: str, source_id: int, actor_id: str) -> list[dict]:
    sent = []
    for item in mentions:
        principal_id = item.get("principal_id")
        if principal_id is None or principal_id == actor_id:
            continue
        event = publish(
            int(team_id),
            "mention.notified",
            {
                "mentioned_principal": principal_id,
                "source_type": source_type,
                "source_id": int(source_id),
            },
        )
        sent.append(event)
    return sent
