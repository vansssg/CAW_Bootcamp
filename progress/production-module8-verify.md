# Production Module 08 VERIFY

Public URL was not claimed. Docker compose failed. Evidence is ASGI + the compose error.

## Checklist

1. Public URL: **missing**. Did not curl a `https://` host. `DEPLOY_BASE_URL` is unset; CI deploy job will not run.
2. `/ready` checks: ASGI `503 {"ok":false,"checks":{"database":"disconnected","cache":"disconnected","uptime_seconds":4}}`. Not `{ok:true}` unconditional. `/ready` 200 **not** observed (Postgres down).
3. `/metrics` ASGI 200, 1346 bytes, contains `http_requests_total`, `http_request_duration_seconds`, `urls_total`.
4. Broken-DB gate: this host’s DATABASE_URL/5432 timeout makes `/ready` 503. There is no load balancer, so “broken version never served public traffic” is only true because there is no public traffic. `/live` still 200 — the CONTEXT lie still exists if someone routed on liveness alone.
5. Rollback clock: **not measured**. `IMAGE_TAG=<sha> docker compose ... up -d app` was not executed (daemon pipe missing).

## Pipeline from push to user (this repo)

1. `git push origin main`
2. GitHub Actions `lint` (ruff) and `test` (`test_query_columns.py`) in parallel
3. `build` needs both: `docker build -t url-shortener:$GITHUB_SHA ./api`
4. `deploy` runs **only if** `vars.DEPLOY_BASE_URL` is set: curl `/ready` until 200, then smoke `/live` `/ready` `/metrics`. On failure, echo local compose rollback (no Railway token).
5. Failures: lint/test fail → no image. Image build fail → no deploy. `/ready` never 200 → deploy job fails, no “walk away green.”
6. User traffic: **there is no step that routes users**. Compose `app` would bind `:3000` if Docker worked.

## Monday morning after Friday 16:00 push

Not “the dashboard.” Look at:
- `GET /ready` JSON `checks.database` (must be `connected` and HTTP 200)
- log line `failure_mode=postgres_connect_or_query_timeout` if 503
- `urls_total` and `http_requests_total{status="5.."}` on `/metrics`
- GitHub Actions for that SHA: did `build` pass, did `deploy` skip because `DEPLOY_BASE_URL` empty?

This weekend: deploy skipped. Service on this laptop is `/live` 200 `/ready` 503.

## Silent memory leak

`/ready` only pings Postgres/Redis. HighLatencyP95 (p95 > 2s for 3m) is the catch we already wrote. Add next: a process RSS gauge and a ready fail if RSS exceeds a cap — **not implemented**. `uptime_seconds` in `/ready` only shows crash loops, not slow leaks.
