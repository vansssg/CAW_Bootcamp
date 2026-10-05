# AI-Augmented Engineering Module 08 VERIFY

Checklist with evidence. GitHub Actions was **not** run this session. Local ASGI suite is measured. Docker/Postgres/Redis not claimed.

## Auth map (current)

| Endpoint | Auth | Authorization |
|----------|------|----------------|
| POST /teams | require_api_key | any principal |
| POST /teams/{id}/invitations | require_api_key | require_team_admin |
| GET /teams/{id}/invitations | require_api_key | require_team_member |
| POST /invitations/{token}/accept | require_api_key | email match + pending |
| PUT /teams/{id}/members/{uid} | require_api_key | require_team_admin + not self |
| POST /teams/{id}/comments | require_api_key | require_commenter (not viewer) |
| GET comments / GET audit / WS | require_api_key | require_team_member |
| PATCH/DELETE comments | require_api_key | member + author |

No new unauthenticated team route this module.

## Input validation

- Team name: non-empty strip. **No max length** (gap).
- Invite email: EMAIL_FORMAT. Role: INVITE_ROLES.
- PUT role: OWNER_SETTABLE_ROLES; admin cannot set owner.
- Comment body: 1–5000.

## Suite (run now)

`python -m app.scripts.module08_team_suite` → `MODULE08_TEAM_SUITE_OK True`; `I_MODULE09_EXIT 0`. Viewer comment 403; cross-team 403; E2E audit pairs present.

## Secrets

API keys loaded from env via `config.py` (min 32 chars). Logs redact emails (`[REDACTED_EMAIL]`). Suite prints statuses, not tokens. Did not dump DATABASE_URL.

## Docs spot-check (same ASGI calls)

1. POST /teams empty → 400 (docs). Measured `E_TEAMS_EMPTY_NAME 400`.
2. POST invite role=owner → 400. Measured `P_INVITE_OWNER_ROLE 400`.
3. GET invitations as viewer → 200 without token. Measured `P_VIEWER_CAN_VIEW_LIST 200` and no tokens.

## CI

Workflow file now includes `module08_team_suite`. **This session did not execute GitHub Actions.** Local equivalent passed. `docker build` CI job not verified locally (engine has been down).

## Rollback

Team store is memory: revert the deploy/image; restart drops in-process teams. No team Alembic to revert. Notify: whoever ships main. Time: one image roll + process restart. Written in `api/docs/team-collaboration.md`.
