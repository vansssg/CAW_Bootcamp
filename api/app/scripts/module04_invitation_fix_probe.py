"""FIX verification: admin create works; non-admin create 403; list IDOR closed."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.invitations import reset_for_tests
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
    admin_status, admin_body = post(
        "/teams/1/invitations",
        API_KEY_A,
        {"email": "fresh.invite@example.com"},
    )
    member_status, _ = post(
        "/teams/1/invitations",
        API_KEY_B,
        {"email": "attacker@example.com"},
    )
    member_list, member_list_body = get("/teams/1/invitations", API_KEY_B)
    _, team = post("/teams", API_KEY_A, {"name": "secret-team"})
    team_id = team["id"]
    post(
        f"/teams/{team_id}/invitations",
        API_KEY_A,
        {"email": "hidden.user@example.com"},
    )
    outsider_list, outsider_body = get(f"/teams/{team_id}/invitations", API_KEY_B)
    outsider_emails = [row.get("email") for row in (outsider_body.get("items") or [])]
    print("FIX_ADMIN_CREATE_STATUS", admin_status)
    print("FIX_ADMIN_CREATE_PENDING", admin_body.get("status") == "pending")
    print("FIX_NON_ADMIN_CREATE_STATUS", member_status)
    print("FIX_MEMBER_LIST_OWN_TEAM_STATUS", member_list)
    print("FIX_MEMBER_LIST_COUNT", len(member_list_body.get("items") or []))
    print("FIX_OUTSIDER_LIST_STATUS", outsider_list)
    print("FIX_OUTSIDER_SAW_HIDDEN_EMAIL", "hidden.user@example.com" in outsider_emails)
    print("FIX_BOTH_REQUIRED_TESTS_OK", admin_status == 200 and member_status == 403)
    print("FIX_LIST_IDOR_CLOSED", outsider_list == 403)


if __name__ == "__main__":
    main()
