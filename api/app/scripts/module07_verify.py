"""VERIFY: role allowlist + cross-team IDOR + module09."""

import json
import subprocess
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
    _, team = post("/teams", API_KEY_A, {"name": "t2"})
    tid = team["id"]
    owner_s, _ = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "owner"},
    )
    super_s, _ = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "superadmin"},
    )
    member_s, member_body = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "member"},
    )
    acc_s, _ = post(f"/invitations/{member_body.get('token')}/accept", API_KEY_B, {})
    print("V_OWNER_ROLE_STATUS", owner_s)
    print("V_SUPERADMIN_ROLE_STATUS", super_s)
    print("V_MEMBER_ROLE_STATUS", member_s)
    print("V_ACCEPT_MEMBER_STATUS", acc_s)
    print("V_B_ROLE", memberships.get((tid, "principal-b")))
    print("V_PRIVILEGE_ESCALATION", memberships.get((tid, "principal-b")) == "owner")

    _, secret = post("/teams", API_KEY_A, {"name": "secret-only-a"})
    sid = secret["id"]
    inv_b, _ = post(f"/teams/{sid}/invitations", API_KEY_B, {"email": "z@example.com"})
    com_b, _ = post(f"/teams/{sid}/comments", API_KEY_B, {"body": "nope"})
    aud_b, _ = get(f"/teams/{sid}/audit", API_KEY_B)
    lis_b, _ = get(f"/teams/{sid}/invitations", API_KEY_B)
    print("V_CROSS_INVITE", inv_b)
    print("V_CROSS_COMMENT", com_b)
    print("V_CROSS_AUDIT", aud_b)
    print("V_CROSS_LIST", lis_b)
    print("V_CROSS_ALL_DENIED", all(s in (401, 403, 404) for s in (inv_b, com_b, aud_b, lis_b)))

    m09 = subprocess.run(
        [sys.executable, "-m", "app.scripts.module09_test_suite"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print("V_MODULE09_EXIT", m09.returncode)


if __name__ == "__main__":
    main()
