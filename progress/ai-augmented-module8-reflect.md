# AI-Augmented Engineering Module 08 REFLECT

DECIDE was **B production-grade**. BREAK was still an environment assumption: CI had no `API_KEY_*`, while this machine has `api/.env`. Production-grade assertions did not catch “Settings loads from a file the pipeline does not have.”

## Completeness

E2E HTTP journey holds: create team (owner) → invite member → accept → comment with mention → audit has team.created, invitation.created, invitation.accepted, comment.created, mention notify (`MODULE08_TEAM_SUITE_OK True`). Viewer cannot comment/invite/self-admin. Cross-team 403.

Known limits (documented): no DELETE team / remove member; WS not in the HTTP suite (feed checked via comments+audit); GitHub Actions not executed here (workspace is not a git repo); Postgres/Redis/Docker not serving.

## Quality (1–5)

- Security **4**: invite role allowlist, PUT constraints, viewer cannot comment. Gaps: GET audit is any member; team name has no max length.
- Maintainability **3**: FastAPI + error envelope consistent; `require_team_admin` 403 still says “team invitation”; camelCase invite helpers vs `create_link`.
- Tests **4**: ASGI suite is environment-independent on teams it creates; CI dummy env measured locally. Not a 5: GH Actions unrun; WS untested in this suite.
- Docs **4**: three spot-checks matched. Guest role: add to `INVITE_ROLES` / `MEMBER_ROLES` / `COMMENT_ROLES` as written in `api/docs/team-collaboration.md`.

## Process

Prompts this module: BUILD (tests/docs/CI), plus targeted CI-env fix. Iterations: one dialect miss (`postgresql://` vs `postgresql+psycopg`), one key-length 31→32. Most common AI issue across the skill: **auth function present, privilege wrong**. Next time: put CI env in the workflow in the same prompt as the test command.

## Time

Wall clock for Operator M7–M8 this session was hours of probe-and-patch, not greenfield typing. Hand-writing the same RBAC would have been similar or slower; the time was review, not keystrokes.

## Meta

The job was deciding what “right” is: membership ≠ admin, list 200 ≠ no token leak, local green ≠ CI can import Settings.

## Knowledge

1. Last mile is tests/docs/CI/rollback that survive an empty checkout.
2. B: full gates — biggest impact was putting `module08_team_suite` in CI **and** giving that job env so Settings can load.
3. Proof: `MODULE08_TEAM_SUITE_OK True`; `FIX_SUITE_OK True`; `I_MODULE09_EXIT 0`.

Mini task: `python -m app.scripts.module08_team_suite` → all OK including E2E audit pairs.

Risk: GH Actions still unrun. Mitigation: dummy env in `ci.yml`; do not claim the hosted pipeline is green.
