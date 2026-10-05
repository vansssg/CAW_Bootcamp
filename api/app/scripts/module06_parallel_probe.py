"""Sequential merge probes for comments, mentions, audit. Never opens DATABASE_URL."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.activity import replay_since, reset_for_tests as reset_activity
from app.audit import entries as audit_entries
from app.audit import reset_for_tests as reset_audit
from app.auth import API_KEY_A, API_KEY_B
from app.comments import reset_for_tests as reset_comments
from app.invitations import reset_for_tests
from app.mentions import parse
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

    parsed = parse("hey @principal-b and @nobody")
    print("AGENT2_PARSE_COUNT", len(parsed))
    print("AGENT2_RESOLVED_B", any(row["principal_id"] == "principal-b" for row in parsed))
    print("AGENT2_UNKNOWN_NULL", any(row["username"] == "nobody" and row["principal_id"] is None for row in parsed))

    a_status, a_body = post(
        "/teams/1/comments",
        API_KEY_A,
        {"body": "ship it @principal-b"},
    )
    print("AGENT1_CREATE_STATUS", a_status)
    print("AGENT1_CREATE_ID", a_body.get("id"))

    b_status, b_body = post(
        "/teams/1/comments",
        API_KEY_B,
        {"body": "ack"},
    )
    print("AGENT1_MEMBER_CREATE_STATUS", b_status)

    _, team = post("/teams", API_KEY_A, {"name": "secret"})
    other_id = team["id"]
    outsider, _ = post(
        f"/teams/{other_id}/comments",
        API_KEY_B,
        {"body": "leak"},
    )
    print("AGENT1_OUTSIDER_CREATE_STATUS", outsider)

    empty, _ = post("/teams/1/comments", API_KEY_A, {"body": ""})
    print("AGENT1_EMPTY_BODY_STATUS", empty)

    types = [row["type"] for row in replay_since(1, None)]
    print("MERGE_COMMENT_CREATED", "comment.created" in types)
    print("MERGE_MENTION_NOTIFIED", "mention.notified" in types)
    mention_payloads = [row.get("payload") or {} for row in replay_since(1, None) if row["type"] == "mention.notified"]
    print("MERGE_MENTION_NO_EMAIL", all("email" not in row for row in mention_payloads))

    audit_status, audit_body = get("/teams/1/audit", API_KEY_A)
    items = audit_body.get("items") or []
    actions = [row.get("action") for row in items]
    resources = [row.get("resource_type") for row in items]
    print("AGENT3_AUDIT_HTTP", audit_status)
    print("AGENT3_AUDIT_HAS_COMMENT", "comment" in resources)
    print("AGENT3_AUDIT_HAS_MENTION", "mention" in resources or "notify" in actions)
    print("AGENT3_AUDIT_EMAIL_LEAK", any("email" in (row.get("metadata") or {}) for row in items))
    print("AGENT3_AUDIT_COUNT", len(items))
    print("AUDIT_ENTRIES_TOTAL", len(audit_entries))

    unauth, _, _ = call("POST", "/teams/1/comments", body=b'{"body":"x"}')
    print("AGENT1_UNAUTH_STATUS", unauth)


if __name__ == "__main__":
    main()
