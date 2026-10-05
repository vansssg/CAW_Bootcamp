# Production Module 08 CONTEXT — deploy verification

Deploying is uploading. Verification is proving the new version serves real traffic. Knight: missed one server. Semicolon-in-URI incident: `/live` 200 while 100% of real requests 500 for 23 minutes.

## 1. What `/live` and `/readyz` actually check

- `GET /live` (`api/app/main.py`): returns `{"ok": true}`. No DB, no Redis, no probe of `/r/{code}`. Observed 2026-08-17: `200` in **0.052s** while Postgres was down.
- `GET /health`: same lie, no DB.
- `GET /readyz`: `SELECT 1` behind pybreaker. Observed: **503** in **4.049s**, `error.code=service_unavailable`, log `postgres_connect_or_query_timeout`.
- Startup `verify_database_connection()` does try `SELECT 1` + `CREATE TABLE IF NOT EXISTS analytics`, but it **catches** the failure and still serves HTTP. So a bad `DATABASE_URL` (semicolon vs colon) would match the CONTEXT story: process up, `/live` 200, writes 503.

What `{ok:true}` on `/live` misses: wrong connection string, Postgres down, Redis down, stale replica still on `/ready`, successful-but-wrong 307s.

## 2. Error rate doubles — who is notified, first two minutes

On this laptop: **nobody is paged**. `progress/production-module4-alert-rules.yml` defines `HighErrorRate` (>5% 5xx for 2m) but there is **no Prometheus scraper** and no Alertmanager. Saying “probably the dashboard” is exactly the fail.

If someone *were* paged: first two minutes are `docs/runbooks/high-error-rate.md` — `/live` vs `/readyz` once (do not loop), then postgres-unreachable or `git revert`. Knight add-on: if `/live` 200 and `/r/{code}` 307 to the wrong place, HighErrorRate stays quiet.

## Honest deploy bound

Not localhost / not CI is the lesson. This workspace: Docker Desktop pipe missing, no Railway, Postgres `TimeoutError` on 5432. CONTEXT does not claim a public URL exists.
