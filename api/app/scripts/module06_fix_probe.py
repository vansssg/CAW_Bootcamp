"""FIX: audit listener registered; comment 403 copy not invitation."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.activity import global_listener_count, reset_for_tests as reset_activity
from app.audit import list_for_team, reset_for_tests as reset_audit
from app.auth import API_KEY_A, API_KEY_B
from app.comments import reset_for_tests as reset_comments
from app.invitations import reset_for_tests
from app.main import audit_mod
from app.scripts.module09_test_suite import call

audit_mod.ensure_listening()


def post(path, key, payload):
    status, _, body = call(
        "POST",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    return status, json.loads(body.decode() or "{}")


def patch(path, key, payload):
    status, _, body = call(
        "PATCH",
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
    audit_mod.ensure_listening()
    status, created = post("/teams/1/comments", API_KEY_A, {"body": "glue @principal-b"})
    cid = created["id"]
    audit = list_for_team(1)
    comment_rows = [row for row in audit if row.get("resource_type") == "comment"]
    b_status, b_body = patch(f"/teams/1/comments/{cid}", API_KEY_B, {"body": "nope"})
    msg = (b_body.get("error") or {}).get("message") or ""
    print("FIX_LISTENER_COUNT", global_listener_count())
    print("FIX_COMMENT_HTTP", status)
    print("FIX_AUDIT_COMMENT_COUNT", len(comment_rows))
    print("FIX_COMMENTS_IN_AUDIT", len(comment_rows) >= 1)
    print("FIX_NON_AUTHOR_403", b_status)
    print("FIX_403_NOT_INVITATION", "invitation" not in msg.lower())
    print("FIX_403_MESSAGE", msg)


if __name__ == "__main__":
    main()
