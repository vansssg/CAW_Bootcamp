# AI-Augmented Engineering Module 08 CONTEXT

Last mile: demo-ready is not shippable. M04 IDOR, M05 WS, M06 glue, M07 privilege writes are patched on this machine. They are not protected for the next engineer.

## What production-ready means here

| Bar | This repo now |
|-----|----------------|
| Regression tests | `module07_fix.py` thirteen PUT cases and invite probes exist locally. CI (`.github/workflows/ci.yml`) runs only `test_query_columns.py` and `module09_test_suite.py` (six link tests). A role-enum regression would stay green. |
| Docs for the next hire | No team-collab README. Adding a role type means reading `invitations.py` (`ADMIN_ROLES`, `INVITE_ROLES`, `MEMBER_ROLES`). |
| CI signal | Lint + those two scripts. `docker build` is a CI job; local `docker info` has been exit 1 — image build is not verified here. |
| Deploy/rollback | Deploy waits on `DEPLOY_BASE_URL` `/ready` 200. Placeholder rollback prints compose with previous SHA. Postgres/Redis still not serving locally. `/ready` has been 503. |

No code generation this step. Gap: team tests and docs are not in the pipeline that runs on every push.
