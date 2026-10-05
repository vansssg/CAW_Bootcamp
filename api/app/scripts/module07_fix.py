"""FIX: thirteen PUT role cases + BREAK composition closed."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.invitations import memberships, reset_for_tests
from app.activity import reset_for_tests as reset_activity
from app.audit import reset_for_tests as reset_audit, entries as audit_entries
from app.comments import reset_for_tests as reset_comments
from app.scripts.module09_test_suite import call
from app.scripts.module07_break_probe import main as break_main


def post(path, key, payload):
    status, _, body = call(
        "POST",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
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
        parsed = {}
    return status, parsed


def new_team():
    reset_for_tests()
    reset_activity()
    reset_comments()
    reset_audit()
    _, team = post("/teams", API_KEY_A, {"name": "fix-roles"})
    return team["id"]


def roles(tid, a_role, b_role):
    memberships[(tid, "principal-a")] = a_role
    memberships[(tid, "principal-b")] = b_role


def main():
    results = []

    tid = new_team()
    roles(tid, "owner", "viewer")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_B, {"role": "admin"})
    results.append(("T01_VIEWER_SELF_ADMIN", s, 403))

    tid = new_team()
    roles(tid, "owner", "viewer")
    s, _ = put(f"/teams/{tid}/members/principal-a", API_KEY_B, {"role": "member"})
    results.append(("T02_VIEWER_OTHER", s, 403))

    tid = new_team()
    roles(tid, "owner", "member")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_B, {"role": "admin"})
    results.append(("T03_MEMBER_SELF_ADMIN", s, 403))

    tid = new_team()
    roles(tid, "owner", "member")
    s, _ = put(f"/teams/{tid}/members/principal-a", API_KEY_B, {"role": "viewer"})
    results.append(("T04_MEMBER_OTHER", s, 403))

    tid = new_team()
    roles(tid, "admin", "viewer")
    s, body = put(f"/teams/{tid}/members/principal-b", API_KEY_A, {"role": "member"})
    results.append(("T05_ADMIN_VIEWER_TO_MEMBER", s, 200))
    print("FIX_T05_ROLE", memberships.get((tid, "principal-b")))

    tid = new_team()
    roles(tid, "admin", "member")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_A, {"role": "viewer"})
    results.append(("T06_ADMIN_MEMBER_TO_VIEWER", s, 200))

    tid = new_team()
    roles(tid, "admin", "member")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_A, {"role": "owner"})
    results.append(("T07_ADMIN_PROMOTE_OWNER", s, 403))

    tid = new_team()
    roles(tid, "admin", "member")
    s, _ = put(f"/teams/{tid}/members/principal-a", API_KEY_A, {"role": "member"})
    results.append(("T08_ADMIN_SELF", s, 403))

    tid = new_team()
    roles(tid, "owner", "member")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_A, {"role": "admin"})
    results.append(("T09_OWNER_MEMBER_TO_ADMIN", s, 200))

    tid = new_team()
    roles(tid, "owner", "member")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_A, {"role": "owner"})
    results.append(("T10_OWNER_PROMOTE_OWNER", s, 200))
    audit_role = any(
        row.get("resource_type") == "member" and row.get("action") == "updated" for row in audit_entries
    )

    tid = new_team()
    roles(tid, "owner", "member")
    s, _ = put(f"/teams/{tid}/members/principal-a", API_KEY_A, {"role": "admin"})
    results.append(("T11_OWNER_SELF", s, 403))

    tid = new_team()
    roles(tid, "owner", "member")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_A, {"role": "superadmin"})
    results.append(("T12_SUPERADMIN", s, 400))

    tid = new_team()
    roles(tid, "owner", "member")
    s, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_A, {"role": ""})
    results.append(("T13_EMPTY_ROLE", s, 400))

    passed = 0
    for name, got, want in results:
        ok = got == want
        passed += int(ok)
        print(name, got, "OK" if ok else f"WANT_{want}")
    print("FIX_THIRTEEN_PASSED", passed)
    print("FIX_THIRTEEN_ALL", passed == 13)
    print("FIX_AUDIT_MEMBER_UPDATED", audit_role)

    print("---BREAK_AFTER_FIX---")
    break_main()


if __name__ == "__main__":
    main()
