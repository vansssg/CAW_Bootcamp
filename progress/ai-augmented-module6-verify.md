# AI-Augmented Engineering Module 06 VERIFY

Three levels, one process. `python -m app.scripts.module06_verify`

## Level 1
Create 200, list 200 count 1, update 200, non-author update **403**, delete 200. Unauth was 401 in the parallel probe.

## Level 2
mention.notified True; comment.created/deleted True; audit (comment, created), (comment, deleted), (mention, notify) all True.

## Level 3
module09 exit 0 OK; parallel probe exit 0. No Postgres migration run. Shared files: `main.py` mounts + `activity.add_global_listener`.

Conflict leftover: non-author 403 **detail** is still “team invitation” — Agent 1 copied invitation copy into comments.
