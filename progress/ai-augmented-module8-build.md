# AI-Augmented Engineering Module 08 BUILD

Prompts: `progress/ai-augmented-module8-build-prompt.md`

## Tests

`python -m app.scripts.module08_team_suite` — ASGI, own reset per case, no DB mocks.

- Endpoints: unauth 401, empty name 400, create 200 owner principal-a, duplicate invite 409, already-member 409
- Permission: member cannot invite/PUT; member can comment; viewer cannot comment/invite/self-admin; viewer GET list has no token
- Cross-team all 403
- E2E: create → invite member → accept → comment @mention → audit pairs include team.created, invitation.created, invitation.accepted, comment.created, mention notify
- `I_MODULE09_EXIT 0`
- `MODULE08_TEAM_SUITE_OK True`

Product fixes this step: `require_commenter` (viewer 403 on POST comment); `team.created` publish; audit records `invitation.accepted`.

## Docs

`api/docs/team-collaboration.md` cross-checked: invite 409 pending, PUT 403 self, GET list omits token, no DELETE team.

## CI

`.github/workflows/ci.yml` test job now runs `python -m app.scripts.module08_team_suite` after module09. Did **not** add Alembic: Postgres is not in this pipeline. Team store is memory.

Docker/Redis/Postgres not claimed.
