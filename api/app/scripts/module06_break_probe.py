"""BREAK: comment.created emitted but audit listener unsubscribed — interface gap."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import activity as activity_mod
from app.activity import replay_since, reset_for_tests as reset_activity
from app.audit import list_for_team, reset_for_tests as reset_audit
from app.auth import API_KEY_A
from app.comments import reset_for_tests as reset_comments
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


def main():
    reset_for_tests()
    reset_activity()
    reset_comments()
    reset_audit()
    saved = list(activity_mod._global_listeners)
    activity_mod._global_listeners.clear()
    try:
        status, created = post("/teams/1/comments", API_KEY_A, {"body": "gap @principal-b"})
        types = [row["type"] for row in replay_since(1, None)]
        audit = list_for_team(1)
        comment_audit = [row for row in audit if row.get("resource_type") == "comment"]
        naive_path_resource = "teams/1/comments".split("/")[0]
        print("BREAK_COMMENT_HTTP", status)
        print("BREAK_BUS_HAS_COMMENT_CREATED", "comment.created" in types)
        print("BREAK_AUDIT_COMMENT_COUNT", len(comment_audit))
        print("BREAK_COMMENTS_MISSING_FROM_AUDIT", len(comment_audit) == 0)
        print("BREAK_NAIVE_MIDDLEWARE_RESOURCE", naive_path_resource)
        print("BREAK_GAP", "emit_without_subscriber")
    finally:
        activity_mod._global_listeners[:] = saved


if __name__ == "__main__":
    main()
