# System Design Module 10 VERIFY

## What breaks if PORT is hardcoded?

Railway injects `PORT`. `--port 3000` while the proxy uses 8080 is a black hole. We use `${PORT:-3000}` (`DOCKER_PORT_FROM_ENV True`). `EXPOSE 3000` does not bind.

## What should health check (and not check)?

`/live` is process-up only: `{ok:true}`, no DB. Measured **200**. It must not `SELECT 1` — that is how a down Postgres becomes a restart loop. Dockerfile HEALTHCHECK and `railway.toml` use `/live`.

## What should readiness check, and why?

`/ready` must fail when the dependency the request path needs is down. Here database is critical: **READY_STATUS 503**, `postgres_connect_or_query_timeout`. Redis is reported, not required. Platform must not send write traffic on 503.

## What does graceful shutdown protect?

In-flight `GET /r` and `POST /links`. SIGTERM: stop new accepts, finish in-flight, dispose pools (`on_shutdown`, `--timeout-graceful-shutdown 30`). Without it, Railway SIGKILL cuts redirects mid-307.

## What timeouts and why?

HTTP keep-alive **5s** (do not hold workers forever). Graceful shutdown **30s**. DB `connect_timeout=1`, `statement_timeout=1000ms`, `pool_timeout=1`. TCP to a closed 5432 still ~5s here — we record that, we do not claim 1s wall time.

## Rollback if a migration fails?

Previous `url-shortener:$SHA`. Restore a DB snapshot. Do **not** `alembic downgrade` after writes. `migrate.sh` is one-off, not CMD.

## Build-time vs runtime config?

Build: Python deps, image tag SHA. Runtime: `PORT`, `DATABASE_URL`, keys from Railway env. A container that used `localhost` for Postgres at runtime would miss the compose hostname `postgres`.
