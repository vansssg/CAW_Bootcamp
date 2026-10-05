# Production Readiness Module 05 FIX

## Missed mode added to FMEA
**Partial failure: DB reads succeed, writes fail** (read replica / read-only primary).  
`GET /r/{code}` is a user read that `INSERT`s analytics, so `/ready` (SELECT 1) can stay green while creates/redirects fail. Transient if failover; permanent until the primary accepts writes. Do not retry writes in a tight loop.

## Handling shipped
- `api/app/db.py`: `connect_timeout=2`, `pool_timeout=2`, `statement_timeout=2000ms`, `pool_pre_ping`.
- Fail-closed **503** `"service temporarily unavailable"` on `/ready`, `POST /links`, redirect **lookup**, admin list/delete when `OperationalError`/timeout.
- Log: `database unavailable` + `failure_mode=postgres_connect_or_query_timeout` + `action=` + `request_id`. No traceback in the client body.
- Startup: OperationalError is logged and **does not** keep the process from serving `/live`/`/metrics`.
- Redirect: lookup fail → 503 (fail-closed, no invented URL). Analytics INSERT fail → `warn` `postgres_write_partial_failure` and still redirect if lookup already succeeded.

## Re-simulation (same DB-down environment, not a new hang study)
Command: `api/.venv/Scripts/python.exe app/scripts/module05_failure_fix_verify.py`

| Path | Before FIX | After FIX |
|---|---|---|
| `GET /live` | 200 | **200** in 0.159s `{"ok":true}` |
| `GET /ready` | hang / TIMEOUT, no 5xx | **503** in **4.271s**, log `action=ready` `ConnectionTimeout` |
| `POST /links` | hang | **503** in 4.894s, body `{"detail":"service temporarily unavailable"}` |
| `GET /r/abc123` | hang | **503** in 4.113s, `action=redirect_lookup` |

`FIX_NO_STACK_TO_USER True`. HighErrorRate can now see `status="503"`.

Not claimed: live read-only Postgres to exercise the analytics warn path; Prometheus `for: 2m`.
