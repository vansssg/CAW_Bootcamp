# Module 06 — Interface contracts (locked before agents)

This app is a FastAPI URL shortener. IDs are integers like `links.id`. Actors are `principal-a` / `principal-b`, not User UUIDs. Memory-backed. Postgres is not serving.

Shared locks (all agents):
- Auth: `require_api_key` then `require_team_member` or `require_team_admin`
- Events: `activity.publish(team_id, type, payload)` shape `{type, team_id, ts, payload}` — **no email in payload**
- Errors: 401 missing key, 403 not member/admin, 400 validation, 404 missing, 409 conflict
- Do not modify `app/auth.py`, `app/db.py`, or invent NOTIFY/Redis

## Agent 1 — Comment threads on teams

CREATES: `api/app/comments.py`, probe later
READS: `invitations.require_team_member`, `activity.publish`
MODIFIES: `api/app/main.py` (mount routes only)

Comment: `{id:int, team_id:int, author_id:str, body:str 1-5000, parent_id:int|null, created_at}`

API: POST/GET `/teams/{team_id}/comments`; PATCH/DELETE `/teams/{team_id}/comments/{comment_id}`
AUTH: member of that team
EVENTS: `comment.created|updated|deleted` payload `{comment_id, team_id, author_id}` — no body, no email

## Agent 2 — @mention parse + notify

CREATES: `api/app/mentions.py`
READS: `invitations.PRINCIPAL_EMAIL` keys as mention usernames (`principal-a`)
MODIFIES: none

`parse(text) -> [{raw, username, principal_id|null, start, end}]`
`notify(mentions, *, team_id, source_type, source_id, actor_id)` publishes `mention.notified` `{mentioned_principal, source_type, source_id}` — no email

Consumer (comments) calls these. Agent 2 does not import comments.

## Agent 3 — Audit log

CREATES: `api/app/audit.py`
READS: activity bus
MODIFIES: `activity.publish` gains `add_global_listener` (integration stud)

Entry: `{id:int, action, resource_type, resource_id, actor_id, metadata:dict, ts}` — metadata must not include email

CONSUMES: bus events `*.created|*.updated|*.deleted` and `mention.notified`
API: GET `/teams/{team_id}/audit` — `require_team_member`

## Integration gap made visible

Agent 1 emits `comment.created`. Agent 3 only sees it if the global listener is registered on `publish`. Sequential merge: comments + probe, then mentions glue + probe, then audit listener + probe.
