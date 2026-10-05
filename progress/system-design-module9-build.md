# System Design Module 09 BUILD

Unit-heavy suite: `python app/scripts/module09_test_suite.py` — stdlib `unittest`, real FastAPI `app` over ASGI, isolated `links` / jobs / cache per test. Does **not** open `DATABASE_URL`. `persisted=memory`.

| Test | Result |
|------|--------|
| create link | 200, code in `links` |
| redirect `GET /r/{code}` (Module 03 prefix) | 307 Location `https://www.example.com/dest` |
| auth | `GET /links/search` 401 without key |
| IDOR | B GET/PATCH/DELETE A's code → 404; code still in `links` |
| retention | 40-day event purged, analytics `clicks=1`, `retention_days=30` |
| URL bypass | `javascript:alert(1)` → 400, store empty |

`Ran 6 tests in 0.605s OK`. Redirect paid ~0.5s Redis ping (`REDIS_DOWN`); that is not a Postgres test DB.
