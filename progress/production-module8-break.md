# Production Module 08 BREAK — three issues (this host)

`/ready` is **not** 200 here (Postgres down). The green-dashboard story still maps onto a split we measured.

## 1. Ready does not test the work path

- `GET /ready` → **503** `checks.database=disconnected` (~4.5s)
- `GET /live` → **200**
- `POST /links` → **200** `persisted=memory` (never INSERT)
- `GET /r/{code}` → **307** from the in-process `links` dict
- `GET /debug/error` → **500** `internal_error`

When Postgres is up, `/ready` would go 200 on `SELECT 1` while creates still only fill `links = {}`. Restart → `/r/{code}` 404, `/ready` still 200. Users report errors; dashboard stays green. Same class as the BREAK prompt. `/debug/error` is a second “work endpoint returns 500 while liveness is fine.”

## 2. Memory climbs, ready ignores it

`IN_MEMORY_LINKS 1` `URLS_TOTAL 1.0` after one create. `links` and cache `_local` have no cap. `/ready` checks database/cache ping only — VERIFY silent-degradation case. `uptime_seconds` does not show RSS.

## 3. Config not from the pipeline

`GIT_SHA_IN_PROCESS UNSET`. Compose hardcodes `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/linkops`, which overrides `api/.env` when the app service runs. A UI/compose edit of that URL is not a git SHA deploy. `APP_ENV=development` `PORT=3000` from local settings, not from `url-shortener:${GITHUB_SHA}`.
