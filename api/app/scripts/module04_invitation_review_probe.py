"""ASGI probe for invitation review findings. Never opens DATABASE_URL."""

import io
import json
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.invitations import EMAIL_OUTBOX, invitations, persist_invitation_sql, reset_for_tests
from app.scripts.module09_test_suite import call


def _post(path, key, payload):
    status, _, body = call(
        "POST",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    return status, json.loads(body.decode() or "{}")


def _get(path, key):
    status, _, body = call("GET", path, headers={"X-API-Key": key})
    return status, json.loads(body.decode() or "{}")


def main():
    reset_for_tests()
    unauth, _, _ = call("POST", "/teams/1/invitations", body=b'{"email":"x@example.com"}')
    print("UNAUTH_STATUS", unauth)

    a_status, a_body = _post(
        "/teams/1/invitations",
        API_KEY_A,
        {"email": "new.user@example.com"},
    )
    print("A_CREATE_STATUS", a_status)
    print("A_CREATE_EMAIL", a_body.get("email"))
    print("A_TOKEN_PRESENT", bool(a_body.get("token")))

    b_status, b_body = _post(
        "/teams/1/invitations",
        API_KEY_B,
        {"email": "leaked@example.com"},
    )
    print("B_MEMBER_CREATE_STATUS", b_status)
    print("B_MEMBER_CREATE_ID", b_body.get("id"))
    print("B_IDOR_CREATE", b_status == 200)

    token = a_body.get("token")
    steal_status, steal_body = _post(f"/invitations/{token}/accept", API_KEY_B, {})
    print("B_ACCEPT_A_INVITE_STATUS", steal_status)
    print("B_ACCEPT_IDOR", steal_status == 200)
    print("B_ACCEPTED_BY", steal_body.get("accepted_by"))

    other_team_status, other_team = _post("/teams", API_KEY_A, {"name": "docs"})
    other_id = other_team.get("id")
    print("OTHER_TEAM_STATUS", other_team_status, "OTHER_TEAM_ID", other_id)
    non_member_status, _nm = _post(
        f"/teams/{other_id}/invitations",
        API_KEY_B,
        {"email": "outsider@example.com"},
    )
    print("VERIFY_4_NON_MEMBER_STATUS", non_member_status)

    legit_status, legit_body = _post(
        f"/teams/{other_id}/invitations",
        API_KEY_A,
        {"email": "b@example.com"},
    )
    legit_token = legit_body.get("token")
    b_ok, b_ok_body = _post(f"/invitations/{legit_token}/accept", API_KEY_B, {})
    print("B_LEGIT_ACCEPT_STATUS", b_ok)
    print("B_LEGIT_ACCEPTED_BY", b_ok_body.get("accepted_by"))

    already_status, already_body = _post(
        "/teams/1/invitations",
        API_KEY_A,
        {"email": "b@example.com"},
    )
    print("VERIFY_1_ALREADY_MEMBER_STATUS", already_status)
    print("VERIFY_1_ALREADY_MEMBER_CODE", (already_body.get("error") or {}).get("code") or already_body.get("error"))

    empty_status, empty_body = _post("/teams", API_KEY_A, {"name": ""})
    space_status, _space = _post("/teams", API_KEY_A, {"name": " "})
    print("VERIFY_2_EMPTY_NAME_STATUS", empty_status)
    print("VERIFY_2_SPACE_NAME_STATUS", space_status)
    print("EMPTY_TEAM_NAME", empty_body.get("name"))

    print("VERIFY_3_UNAUTH_STATUS", unauth)
    print("VERIFY_4_MEMBER_NOT_ADMIN_STATUS", b_status)

    invalid_email_status, _inv = _post(
        "/teams/1/invitations",
        API_KEY_A,
        {"email": "not-an-email"},
    )
    print("VERIFY_5_INVALID_EMAIL_STATUS", invalid_email_status)
    print("SELF_INVITE_STATUS", already_status)

    sql, params = persist_invitation_sql(1, "x@example.com'; DROP TABLE teams;--")
    print("SQL_INTERPOLATED", "DROP TABLE" in sql)
    print("SQL_HAS_BIND", ":invited_email" in sql and "DROP TABLE" not in sql)
    print("SQL_PARAM_KEYS", sorted(params.keys()))

    reset_for_tests()
    os.environ["INVITE_EMAIL_FAIL"] = "1"
    try:
        fail_status, fail_body = _post(
            "/teams/1/invitations",
            API_KEY_A,
            {"email": "rollback@example.com"},
        )
    finally:
        os.environ.pop("INVITE_EMAIL_FAIL", None)
    leftover = [
        row for row in invitations.values() if row.get("email") == "rollback@example.com"
    ]
    print("EMAIL_FAIL_HTTP", fail_status)
    print("EMAIL_FAIL_STILL_PENDING", bool(leftover) and leftover[0].get("status") == "pending")
    print("EMAIL_FAIL_SENT_FLAG", fail_body.get("email_sent"))
    print("OUTBOX_COUNT", len(EMAIL_OUTBOX))

    missing, missing_body = _get("/teams/999/invitations", API_KEY_A)
    print("MISSING_TEAM_STATUS", missing)
    print("MISSING_TEAM_HAS_ERROR", "error" in missing_body or missing == 404)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logging.getLogger("app").addHandler(handler)
    reset_for_tests()
    _post("/teams/1/invitations", API_KEY_A, {"email": "pii.user@example.com"})
    log_blob = stream.getvalue()
    logging.getLogger("app").removeHandler(handler)
    print("LOG_LEAKS_EMAIL", "pii.user@example.com" in log_blob)


if __name__ == "__main__":
    main()
