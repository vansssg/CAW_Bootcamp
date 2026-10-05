# Team Collaboration

Memory-backed FastAPI routes on the URL shortener. Team data is **not** in Postgres. `DATABASE_URL` is unused for these handlers. Auth is `X-API-Key` (`API_KEY_A` → `principal-a`, `API_KEY_B` → `principal-b`). Errors: `{error:{code,message,request_id}}`.

## Setup (fresh clone, API only)

1. `cd api`
2. Create a venv and `pip install -r requirements.txt`
3. Copy env so `API_KEY_A` and `API_KEY_B` are set (see existing config)
4. Run `python -m app.scripts.module08_team_suite` — ASGI, no Docker, no Redis, no Postgres
5. Optional: `python -m app.scripts.module09_test_suite` for link tests

Do not run Alembic for this feature. CI does not migrate; the team store is in-process dicts.

## API

| Method | Path | Auth | Authorization | Body | Success | Errors |
|--------|------|------|---------------|------|---------|--------|
| POST | `/teams` | API key | any principal | `{name}` non-empty | 200 `{id,name,owner}` | 401, 400 empty name |
| POST | `/teams/{id}/invitations` | API key | owner/admin | `{email, role?}` role `member`\|`viewer` | 200 invitation (create response includes token) | 403, 400 invalid role/email, 409 already member or pending, 404 |
| GET | `/teams/{id}/invitations` | API key | any member including viewer | — | 200 `{items}` **without** `token` | 403, 404 |
| POST | `/invitations/{token}/accept` | API key | email must match principal | `{}` | 200 | 403 mismatch, 409 already member, 404 |
| PUT | `/teams/{id}/members/{user_id}` | API key | owner/admin, not self | `{role}` `admin`\|`member`\|`viewer`; owner may set `owner` | 200 `{user_id,role,old_role}` | 403 self or non-admin or admin→owner, 400, 404 |
| POST | `/teams/{id}/comments` | API key | owner/admin/member, **not viewer** | `{body, parent_id?}` 1–5000 | 200 comment | 403, 400, 404 parent |
| GET | `/teams/{id}/comments` | API key | any member | — | 200 `{items}` | 403 |
| PATCH/DELETE | `/teams/{id}/comments/{id}` | API key | member + author | PATCH `{body}` | 200 | 403, 404 |
| GET | `/teams/{id}/audit` | API key | any member | — | 200 `{items}` | 403 |
| WS | `/ws/teams/{id}/activity` | API key header | any member | — | events `{type,team_id,ts,payload}` | close 4401/4403 |

Example: `POST /teams` with `X-API-Key` → `{id:2,name:"ship",owner:"principal-a"}`.

There is no `DELETE /teams/{id}` and no `DELETE` member. Those matrix cells are unshipped; they are not 200.

## ADR

- **RBAC:** Invite cannot mint `owner`/`admin`. PUT is the role write: admin/owner only, no self-modify, admin cannot mint owner. Reason: M07 `role=owner` on invite was privilege escalation.
- **Activity:** In-process pub/sub + WebSocket, not Postgres NOTIFY (5432 not serving).
- **Audit:** Global listener on the bus. No email in payload. `invitation.accepted` is recorded even though the type is not `*.created`.
- **Comments:** Viewers may read, not write. Members may comment.

## Rollback

CI deploy job has no platform token. Local note: previous image tag via compose. This feature is memory; restart drops teams.
