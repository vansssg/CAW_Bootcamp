# Production Module 08 BUILD

Local fallback path. No Railway/Fly/Render account used. Docker Desktop engine pipe missing — compose did not start.

## Chunk 1 — platform / secrets

- Chose local compose as the deploy action: `docker compose -f infra/docker-compose.yml up -d --build app` (`infra/deploy-local.sh`, image `url-shortener:${IMAGE_TAG}`).
- Added `app` service; `DATABASE_URL` inside the compose network is `postgres:5432` (not the host localhost URL).
- Secret names (values not printed): APP_ENV PORT DATABASE_URL REDIS_URL LOG_LEVEL JWT_SECRET CORS_ORIGIN API_KEY_A API_KEY_B from `api/.env.example`. Runtime inject is compose `env_file` + environment overrides. No platform secret UI exists here.
- Compose attempt 2026-08-17: `unable to get image 'redis:7-alpine': open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` COMPOSE_EXIT 1.

## Chunk 2 — /live vs /ready

- `/live` still `{ok:true}` no DB. Dockerfile HEALTHCHECK now `/live` (was `/health`).
- `/ready` restored and `/readyz` kept on the same handler. Body `{ok, checks:{database,cache,uptime_seconds}}`. Database disconnected → 503. Redis reported but not required (in-process cache fallback).
- ASGI smoke: `/live 200`; `/ready 503 {"ok":false,"checks":{"database":"disconnected","cache":"disconnected","uptime_seconds":4}}`; `/readyz` same status; `/metrics` 200.

Pause: `/ready` is still ~4.0–4.5s when TCP 5432 times out despite `connect_timeout=1`. Platform probe timeout of 5s is one slow query from flapping. Do not loop `/ready` in CI more often than needed.

## Chunk 3 — pipeline

`.github/workflows/ci.yml`: `build` job `needs: [lint, test]` tags `url-shortener:${{ github.sha }}`. `deploy` job `needs: [build]` and **only runs if** `vars.DEPLOY_BASE_URL` is set. This repo has no platform token. Friday 5 PM push to main does **not** ship to a public URL.

Stance: no automatic production traffic without `DEPLOY_BASE_URL`. Trusting `/live` alone is how the 23-minute incident happens.

## Chunk 4 / failure-first

Cannot push a broken `/ready` to a public URL. The failure-first drill is already this host: DATABASE_URL points at a down 5432, `/ready` 503 with `database: disconnected`. There is no old replica keeping traffic — no public router. Rollback command that exists: `IMAGE_TAG=<previous_sha> docker compose -f infra/docker-compose.yml up -d app` — **untested** because the daemon is down. Timed rollback: not measured.
