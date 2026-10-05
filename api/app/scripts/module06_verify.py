"""Level 1-3 verify for parallel merge. Combined suites. No DATABASE_URL."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.activity import replay_since, reset_for_tests as reset_activity
from app.audit import list_for_team, reset_for_tests as reset_audit
from app.auth import API_KEY_A, API_KEY_B
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


def patch(path, key, payload):
    status, _, body = call(
        "PATCH",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    return status, json.loads(body.decode() or "{}")


def delete(path, key):
    status, _, body = call("DELETE", path, headers={"X-API-Key": key})
    return status, json.loads(body.decode() or "{}")


def get(path, key):
    status, _, body = call("GET", path, headers={"X-API-Key": key})
    return status, json.loads(body.decode() or "{}")


def main():
    reset_for_tests()
    reset_activity()
    reset_comments()
    reset_audit()

    created_s, created = post("/teams/1/comments", API_KEY_A, {"body": "hey @principal-b"})
    cid = created["id"]
    listed_s, listed = get("/teams/1/comments", API_KEY_A)
    upd_s, _ = patch(f"/teams/1/comments/{cid}", API_KEY_A, {"body": "edited @principal-b"})
    b_edit, b_edit_body = patch(f"/teams/1/comments/{cid}", API_KEY_B, {"body": "stolen"})
    del_s, _ = delete(f"/teams/1/comments/{cid}", API_KEY_A)
    types = [row["type"] for row in replay_since(1, None)]
    audit = list_for_team(1)
    audit_actions = {(row["resource_type"], row["action"]) for row in audit}

    print("L1_CREATE", created_s)
    print("L1_LIST", listed_s, "COUNT", len(listed.get("items") or []))
    print("L1_UPDATE", upd_s)
    print("L1_NON_AUTHOR_UPDATE", b_edit, "DETAIL", (b_edit_body.get("error") or {}).get("message"))
    print("L1_DELETE", del_s)
    print("L2_MENTION_EVENT", "mention.notified" in types)
    print("L2_COMMENT_CREATED_EVENT", "comment.created" in types)
    print("L2_COMMENT_DELETED_EVENT", "comment.deleted" in types)
    print("L2_AUDIT_COMMENT_CREATED", ("comment", "created") in audit_actions)
    print("L2_AUDIT_COMMENT_DELETED", ("comment", "deleted") in audit_actions)
    print("L2_AUDIT_MENTION", ("mention", "notify") in audit_actions)
    print("L3_SHARED_FILES", "main.py routes + activity.add_global_listener")
    print("L3_NO_POSTGRES_MIGRATION_RUN", True)

    m09 = subprocess.run(
        [sys.executable, "-m", "app.scripts.module09_test_suite"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print("L3_MODULE09_EXIT", m09.returncode)
    print("L3_MODULE09_OK", m09.returncode == 0 and "OK" in (m09.stderr + m09.stdout))

    par = subprocess.run(
        [sys.executable, "-m", "app.scripts.module06_parallel_probe"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print("L3_PARALLEL_PROBE_EXIT", par.returncode)


if __name__ == "__main__":
    main()
