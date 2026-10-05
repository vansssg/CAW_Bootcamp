# System Design Module 10 BREAK

Hard: platform healthcheck on `/ready` while dependencies are unreachable.

CONTEXT already named this: a “healthy” process restarting because the check path was wrong. VERIFY measured `/live` **200** and `/ready` **503** (`database=disconnected`, ~4.5s, `postgres_connect_or_query_timeout`). Injected that 503 into the **liveness** path of the single container.

## Inject

- `api/Dockerfile` HEALTHCHECK `urlopen .../ready`
- `railway.toml` `healthcheckPath = "/ready"`

Did not start Railway, Docker, or compose.

## Symptom (`module10_break_probe.py`)

- LIVE_STATUS **200**
- READY_STATUS **503** READY_OK False READY_DATABASE disconnected
- DOCKER_HEALTHCHECK_TARGET `/ready` RAILWAY_HEALTHCHECK_TARGET `/ready`
- PROBE_STATUS_IF_HEALTHCHECK **503**
- PLATFORM_WOULD_KILL_SINGLE_CONTAINER **True**

DECIDE A: one process is API + in-process worker. A `/ready` liveness loop restarts the **whole** rollback unit (`url-shortener:$SHA`), including redirects that do not need Postgres (`persisted=memory`). CI `test "$READY" = "200"` is the same class if `DEPLOY_BASE_URL` were set — that job was **not** run (no public URL).
