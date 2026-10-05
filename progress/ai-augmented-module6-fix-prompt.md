# Module 06 FIX prompt (glue)

Do not rewrite comments or audit.

In `api/app/main.py`, after importing `audit_mod`, call `audit_mod.ensure_listening()` so Agent 3 is subscribed to `activity.publish` before any route runs. Agent 3 must consume `comment.created` from the bus, not from the first path segment (`teams`).

Also in `api/app/comments.py`, change non-author 403 detail from the invitation copy to `You are not allowed to modify this comment.`

Fixed means: POST comment 200, GET `/teams/1/audit` includes resource_type comment, `global_listener_count() >= 1`, non-author PATCH 403 message does not contain `invitation`.
