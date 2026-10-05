# AI-Augmented Engineering Module 06 BUILD

Interface-first, sequential merge. Three agents, no circular deps. Postgres/Redis/Docker not used.

## Contracts

`progress/ai-augmented-module6-contracts.md` — integer ids, principal strings, no email in events, `require_team_member`.

## Sequential integration

1. Agent 1 comments → POST/GET `/teams/{id}/comments`
2. Glue: `create_comment` calls `mentions.parse` + `notify` (Agent 2 does not import comments)
3. Agent 3 `add_global_listener` on `activity.publish` so `comment.created` reaches audit

## Probe (`python -m app.scripts.module06_parallel_probe`)

- AGENT2_PARSE_COUNT 2; RESOLVED_B True; UNKNOWN_NULL True
- AGENT1_CREATE_STATUS 200; MEMBER 200; OUTSIDER 403; EMPTY 400; UNAUTH 401
- MERGE_COMMENT_CREATED True; MERGE_MENTION_NOTIFIED True; MERGE_MENTION_NO_EMAIL True
- AGENT3_AUDIT_HTTP 200; HAS_COMMENT True; HAS_MENTION True; EMAIL_LEAK False

Known merge leftover (not fixed here): comment update/delete 403 detail still says "team invitation" (copied invitation helper text).
