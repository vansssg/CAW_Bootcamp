# System Design Module 10 BUILD

Single-container deploy (`A`). Dockerfile already bound `0.0.0.0` and `${PORT:-3000}`. Added keep-alive 5s, graceful shutdown 30s, shutdown dispose, PR CI + module09 suite, Railway env list, one-off `alembic upgrade head` (not in CMD).

Compose app uses hostname `postgres`, not localhost — the Docker networking lesson. Docker engine is still down; no `compose up`, no Railway push.

## Evidence (`module10_deploy_verify.py`)

- DOCKER_HOST_ALL_INTERFACES True, PORT from env, timeouts True, HEALTHCHECK `/live`
- CI_ON_PULL_REQUEST True, CI_RUNS_MODULE09 True
- RAILWAY_HEALTH_LIVE True (`/live`); release gate remains `/ready`
- COMPOSE_APP_USES_POSTGRES_HOSTNAME True
- SHUTDOWN_HANDLER True, MIGRATE_ONE_OFF True
- DB_CONNECT_TIMEOUT_S 1, STATEMENT 1000ms
- LIVE_STATUS 200, READY_STATUS 503 (5432 timeout ~5.2s)
- Rollback: previous `url-shortener:$SHA` (CI already prints this). No platform token.

## Rollback if migration fails

Do not `alembic downgrade` after writes. Restore a snapshot, redeploy previous image. `migrate.sh` is one-off only.
