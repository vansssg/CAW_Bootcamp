# Module 07 FIX — documentation, then full re-walk

## Divergence

BREAK Step 2 (`asgi_request('/ready')`) returned `404 0.008 {"detail":"Not Found"}`. The runbook only had 503~4s (Postgres) or 200 (healthy). The process that answered `/live` 200 no longer had `/ready`; `app/main.py` line 395 is `@app.get("/readyz")`.

This is not a compiler error. The command syntax was fine. The path was stale.

## Doc updates (not a silent code revert)

- Probe commands now call `/readyz`.
- Added Step 2b: print `@app.get("/ready` lines from `app/main.py` when the probe 404s.
- `docs/service-overview.md` endpoints + deploy curls now list `/readyz`.
- high-error-rate and high-latency runbooks updated to the same path.

Did **not** restore `/ready` in code. The FIX lesson is to update the runbook to the system that exists.

## Re-test (updated runbook, top to bottom, 2026-08-17)

| Step | Actual |
|---|---|
| 1 `/live` | `200 {"ok":true}` |
| 2 `/readyz` | `status 503 secs 4.049` body `error.code=service_unavailable` `failure_mode=postgres_connect_or_query_timeout` |
| 2b route table | `395 @app.get("/readyz")` |
| stale `/ready` | still `404 0.009` — Step 2b exists so this is now a branch, not a dead end |
| 3 `docker ps` | `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` |
| 4 TCP 5432 | `TimeoutError: timed out` |
| Fix compose | **not run** — daemon down, runbook says stop |
| Verify `/live` | `live 200` |
| `/readyz` after start | never 200 — Postgres did not start |

The corrected runbook now matches: 503 on `/readyz` is Postgres; 404 on `/ready` is path drift; Docker down means escalate, not invent a start.

## How would this have been found at 3 AM?

It would not, until Step 2 404'd and the on-call had no row. Scheduled re-walks after health-route deploys, and updating the runbook after every incident that used it, are the only detection. A wiki paragraph about “readiness” would not have caught `/ready` → `/readyz`.
