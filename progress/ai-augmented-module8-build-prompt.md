# Module 08 BUILD prompts

## Tests

Generate `api/app/scripts/module08_team_suite.py` using ASGI `call()` like `module09_test_suite.py`. Do not open DATABASE_URL. Each case resets team stores. Assert status AND membership/audit state.

Must include: POST /teams 401/400/200+owner; invite 403 for non-admin; duplicate pending 409; already-member 409; role=owner 400; accept 200 role=member; member cannot invite or PUT roles; member can comment; viewer can GET list without tokens, cannot comment/invite/PUT self admin; cross-team all 403; E2E A create → invite B member → accept → comment @principal-a → A sees comment and audit (team.created, invitation.created, invitation.accepted, comment.created, mention notify). Then module09 exit 0.

Do not mock require_team_admin.

## Docs

Write `api/docs/team-collaboration.md` matching actual routes and status codes. Setup: venv, no Postgres required for team store (memory). ADR: RBAC enums, WS vs polling, audit via activity bus.

## CI

Add `python -m app.scripts.module08_team_suite` to `.github/workflows/ci.yml` test job after module09. Do not add alembic against DATABASE_URL — that host is not in this pipeline and has not been serving locally.
