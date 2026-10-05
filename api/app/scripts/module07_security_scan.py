"""Module 07 hybrid security scan. ASGI only. Never opens DATABASE_URL."""

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


def main():
    reset_for_tests()
    reset_activity()
    reset_comments()
    reset_audit()

    b_invite, _ = post(
        "/teams/1/invitations",
        API_KEY_B,
        {"email": "x@example.com", "role": "owner"},
    )
    print("SCAN_B_INVITE_OWNER_STATUS", b_invite)

    _, team = post("/teams", API_KEY_A, {"name": "priv"})
    tid = team["id"]
    a_status, a_body = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "owner"},
    )
    print("SCAN_A_INVITE_OWNER_STATUS", a_status)
    print("SCAN_A_INVITE_ROLE", a_body.get("role"))
    token = a_body.get("token")
    acc_s, acc = post(f"/invitations/{token}/accept", API_KEY_B, {})
    print("SCAN_B_ACCEPT_OWNER_STATUS", acc_s)
    print("SCAN_B_ROLE_AFTER_ACCEPT", memberships.get((tid, "principal-b")))
    print("SCAN_PRIVILEGE_ESCALATION", memberships.get((tid, "principal-b")) == "owner")

    listed_s, listed = get("/teams/1/invitations", API_KEY_B)
    tokens = [row.get("token") for row in (listed.get("items") or [])]
    print("SCAN_B_LIST_STATUS", listed_s)
    print("SCAN_B_LIST_HAS_TOKEN", any(tokens))

    wild_s, wild = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "wild.user@example.com", "role": "superadmin"},
    )
    print("SCAN_ROLE_SUPERADMIN_STATUS", wild_s)
    print("SCAN_ROLE_SUPERADMIN_STORED", wild.get("role"))


if __name__ == "__main__":
    main()
