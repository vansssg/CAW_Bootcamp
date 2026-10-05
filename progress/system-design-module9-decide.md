# System Design Module 09 DECIDE

Choice: **A** (`decisions.module_09.test_strategy = unit_heavy`)

Most expensive failures here (empty API key 401, DELETE then GET /r 404, recreate clicks not doubled) live in the FastAPI process, not in Postgres. `localhost:5432` and `:6379` do not serve; Docker compose cannot start. An integration-heavy suite that requires a real DB would be skipped or would hang ~4s per connect — the same class as a test that pointed at the wrong `DATABASE_URL`.

Tradeoff: we do **not** trust mocks of `get_redirect_target` (that hid Bug 9). Unit-heavy means: real `app` via ASGI, real `links` OrderedDict, **no** MagicMock cache/DB. We will not claim a Testcontainers Postgres. B would be right when CI can run `links_fts.sql` against a disposable DB; it cannot today.
