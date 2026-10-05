# System Design Module 09 CONTEXT

Tests are how we ship; isolation is how tests do not become the incident.

## 1. If only one test today

**Create a link, `GET /r/{code}` must 307 with that `Location`, then `DELETE` and `GET /r/{code}` must 404.**

Wrong redirects are listed as a security incident. This service already had cache-first 307 after SoT removal (Debugging M06). Auth bypass was SEV1, but redirect is the public path — no API key. One test that pins DELETE→404 also guards `cache_sot_mismatch`. `module08_search_verify.py` does not cover this; `module06_break_recreate.py` does.

## 2. Fastest way a test hits a real database

Load `DATABASE_URL` from `api/.env` (or CI secrets) and run a script that `create_engine` + `INSERT`. `app/scripts/module-02-seed-query.py` hardcodes `postgresql+psycopg://postgres:postgres@localhost:5432/upsk_sdf`. One wrong env and pytest is the GitLab wipe analogue. Isolation: search/create tests use the in-memory `links` map and ASGI; they must not set `SEARCH_USE_POSTGRES=1` or `JOB_PERSIST_DB=1` in CI. `test_query_columns.py` only string-asserts the seed file — it does not connect. We still will not claim 5432 is empty; we just do not open it.
