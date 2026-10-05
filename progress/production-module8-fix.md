# Production Module 08 FIX

Used M04 metrics (`urls_total`, `/metrics`), M04 logs (`persisted=memory`, `postgres_connect_or_query_timeout`), M07 postgres runbook (not this incident — `/ready` 503 is DB; the user-visible split is memory SoT). Added `docs/runbooks/ready-green-users-failing.md`.

## 1. Ready vs work

Left `/ready` as dependency gating (`SELECT 1` + cache report). Added post-deploy business smoke in `api/app/scripts/module08_deploy_smoke.py`: `POST /links` + `GET /r/{code}`. Observed after fix: LIVE 200, READY 503 with `image_sha` + `in_memory_links`, POST 200 `persisted=memory`, REDIRECT 307. `/debug/error` is 404 when `APP_ENV=production` (this host is development, still 500).

## 2. Memory

`links` is now `OrderedDict` with `MAX_IN_MEMORY_LINKS=10000` FIFO. Cache `_local` capped at 1000. Jobs `_events` / `_seen_job_ids` capped at 10000. `urls_total` already exists; `/ready` now reports `in_memory_links`.

## 3. Config drift

`IMAGE_SHA` from `IMAGE_TAG` or `GITHUB_SHA` (else `unknown`) is in `/ready` checks. Compose injects `IMAGE_TAG`. Do not edit `DATABASE_URL` in a UI; redeploy a tagged image. This process still shows `image_sha=unknown` because we did not start compose.

## Deploy cycle not run

Did **not** `git push origin main`. Docker daemon still missing `dockerDesktopLinuxEngine`. `/ready` 200 not observed. Rollback still untimed.
