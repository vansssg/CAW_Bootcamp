"""Team invitation first-pass store and handlers. Memory-backed; Postgres is not serving."""

from __future__ import annotations

import os
import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

PRINCIPAL_EMAIL = {
    "principal-a": "a@example.com",
    "principal-b": "b@example.com",
}

INVITE_TTL_HOURS = 72
EMAIL_OUTBOX: list[dict] = []
EMAIL_FORMAT = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ADMIN_ROLES = frozenset({"owner", "admin"})
INVITE_ROLES = frozenset({"member", "viewer"})
teams: dict[int, dict] = {}
memberships: dict[tuple[int, str], str] = {}
invitations: dict[int, dict] = {}
_next_team_id = 1
_next_invite_id = 1


def _now() -> datetime:
    return datetime.now(timezone.utc)


def reset_for_tests() -> None:
    global _next_team_id, _next_invite_id
    teams.clear()
    memberships.clear()
    invitations.clear()
    EMAIL_OUTBOX.clear()
    _next_team_id = 1
    _next_invite_id = 1
    from app.activity import reset_for_tests as reset_activity

    reset_activity()
    seed_default_team()


def seed_default_team() -> None:
    global _next_team_id
    if 1 in teams:
        return
    teams[1] = {"id": 1, "name": "platform", "owner": "principal-a"}
    memberships[(1, "principal-a")] = "owner"
    memberships[(1, "principal-b")] = "member"
    _next_team_id = max(_next_team_id, 2)


seed_default_team()


def _email_owner_on_team(team_id: int, email_norm: str) -> str | None:
    for (tid, principal_id), _role in memberships.items():
        if tid != int(team_id):
            continue
        mapped = PRINCIPAL_EMAIL.get(principal_id, "").strip().casefold()
        if mapped == email_norm:
            return principal_id
    return None


def send_invitation_email(email: str, token: str) -> None:
    if os.getenv("INVITE_EMAIL_FAIL") == "1":
        raise RuntimeError("email service down")
    EMAIL_OUTBOX.append({"email": email, "token": token})


def persist_invitation_sql(team_id: int, email: str) -> tuple[str, dict]:
    sql = "INSERT INTO team_invitations (team_id, invited_email) VALUES (:team_id, :invited_email)"
    params = {"team_id": int(team_id), "invited_email": email}
    return sql, params


def require_team_admin(team_id: int, principal_id: str) -> str:
    role = memberships.get((int(team_id), principal_id))
    if role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to perform this action on this team invitation.",
        )
    return role


def createInvitation(team_id, email, principal_id, role="member"):
    data = teams.get(int(team_id))
    if data is None:
        raise HTTPException(status_code=404, detail="Team not found")
    require_team_admin(int(team_id), principal_id)
    role_norm = str(role or "member").strip().casefold()
    if role_norm not in INVITE_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    email_norm = str(email or "").strip().casefold()
    if EMAIL_FORMAT.match(email_norm) is None:
        raise HTTPException(status_code=400, detail="Invalid email format")
    if _email_owner_on_team(int(team_id), email_norm) is not None:
        raise HTTPException(status_code=409, detail="Already a team member")
    if _pending_invite_for_email(int(team_id), email_norm) is not None:
        raise HTTPException(status_code=409, detail="Invitation already pending")
    persist_invitation_sql(team_id, email_norm)
    global _next_invite_id
    invite_id = _next_invite_id
    _next_invite_id += 1
    token = secrets.token_urlsafe(16)
    result = {
        "id": invite_id,
        "team_id": int(team_id),
        "email": email_norm,
        "role": role_norm,
        "token": token,
        "status": "pending",
        "invited_by": principal_id,
        "created_at": _now().isoformat().replace("+00:00", "Z"),
        "expires_at": (_now() + timedelta(hours=INVITE_TTL_HOURS)).isoformat().replace("+00:00", "Z"),
    }
    invitations[invite_id] = result
    try:
        send_invitation_email(email_norm, token)
        result["email_sent"] = True
    except Exception:
        invitations.pop(invite_id, None)
        raise HTTPException(status_code=503, detail="invitation email failed")
    from app.activity import publish as publish_activity

    publish_activity(
        int(team_id),
        "invitation.created",
        {"invitation_id": invite_id, "invited_by": principal_id, "role": role_norm},
    )
    return result


def _pending_invite_for_email(team_id: int, email_norm: str) -> dict | None:
    for row in invitations.values():
        if (
            row["team_id"] == int(team_id)
            and str(row.get("email") or "").strip().casefold() == email_norm
            and row.get("status") == "pending"
        ):
            return row
    return None


def _public_invitation(row: dict) -> dict:
    return {key: value for key, value in row.items() if key != "token"}


def require_team_member(team_id: int, principal_id: str) -> str:
    role = memberships.get((int(team_id), principal_id))
    if role is None:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to perform this action on this team invitation.",
        )
    return role


COMMENT_ROLES = frozenset({"owner", "admin", "member"})


def require_commenter(team_id: int, principal_id: str) -> str:
    role = require_team_member(int(team_id), principal_id)
    if role not in COMMENT_ROLES:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to comment on this team.",
        )
    return role


def listInvitations(team_id, principal_id):
    data = teams.get(int(team_id))
    if data is None:
        raise HTTPException(status_code=404, detail="Team not found")
    require_team_member(int(team_id), principal_id)
    return [_public_invitation(row) for row in invitations.values() if row["team_id"] == int(team_id)]


def acceptInvitation(token, principal_id):
    invitation = None
    for row in invitations.values():
        if row["token"] == token:
            invitation = row
            break
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    expected = PRINCIPAL_EMAIL.get(principal_id, "").strip().casefold()
    invited = str(invitation.get("email") or "").strip().casefold()
    if expected == "" or invited != expected or invitation.get("status") != "pending":
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to perform this action on this team invitation.",
        )
    if (invitation["team_id"], principal_id) in memberships:
        raise HTTPException(status_code=409, detail="Already a team member")
    invitation["status"] = "accepted"
    invitation["accepted_by"] = principal_id
    memberships[(invitation["team_id"], principal_id)] = invitation["role"]
    from app.activity import publish as publish_activity

    publish_activity(
        invitation["team_id"],
        "invitation.accepted",
        {"invitation_id": invitation["id"], "accepted_by": principal_id},
    )
    return invitation


def create_team(name: str, principal_id: str) -> dict:
    if name is None or not str(name).strip():
        raise HTTPException(status_code=400, detail="Team name is required")
    global _next_team_id
    team_id = _next_team_id
    _next_team_id += 1
    teams[team_id] = {"id": team_id, "name": str(name).strip(), "owner": principal_id}
    memberships[(team_id, principal_id)] = "owner"
    from app.activity import publish as publish_activity

    publish_activity(
        team_id,
        "team.created",
        {"id": team_id, "author_id": principal_id, "name": teams[team_id]["name"]},
    )
    return teams[team_id]


MEMBER_ROLES = frozenset({"admin", "member", "viewer"})
OWNER_SETTABLE_ROLES = MEMBER_ROLES | {"owner"}


def update_member_role(team_id: int, user_id: str, principal_id: str, role: str) -> dict:
    data = teams.get(int(team_id))
    if data is None:
        raise HTTPException(status_code=404, detail="Team not found")
    requester_role = require_team_admin(int(team_id), principal_id)
    target_id = str(user_id or "").strip()
    if target_id == "" or target_id == principal_id:
        raise HTTPException(status_code=403, detail="Cannot modify your own role.")
    old_role = memberships.get((int(team_id), target_id))
    if old_role is None:
        raise HTTPException(status_code=404, detail="Member not found")
    role_norm = str(role or "").strip().casefold()
    if role_norm not in OWNER_SETTABLE_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    if requester_role != "owner" and role_norm == "owner":
        raise HTTPException(status_code=403, detail="Only owners can create other owners.")
    if requester_role != "owner" and role_norm not in MEMBER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    memberships[(int(team_id), target_id)] = role_norm
    from app.activity import publish as publish_activity

    publish_activity(
        int(team_id),
        "member.updated",
        {
            "id": target_id,
            "target_user_id": target_id,
            "old_role": old_role,
            "new_role": role_norm,
            "author_id": principal_id,
            "team_id": int(team_id),
        },
    )
    return {
        "team_id": int(team_id),
        "user_id": target_id,
        "old_role": old_role,
        "role": role_norm,
        "updated_by": principal_id,
    }
