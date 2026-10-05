# System Design Module 10 FIX

Misconfiguration: HEALTHCHECK and `railway.toml` `healthcheckPath` used `/ready`. VERIFY already showed that path is **503** when 5432 times out, so a platform liveness loop would restart the **single container** (DECIDE A) while `/live` was 200.

Mitigation: liveness = `/live`; readiness = `/ready` (still 503 + `database=disconnected`). Rollback unit remains one image SHA. `on_shutdown` + `--timeout-graceful-shutdown 30` unchanged.

## Proof (not a container curl)

`docker info` exit 1 — engine not usable; no `docker run`, no Railway.

`module10_fix_probe.py` (ASGI stand-in for curl):

- DOCKER_HEALTHCHECK_TARGET `/live` RAILWAY_HEALTHCHECK_TARGET `/live`
- LIVE_STATUS **200** PROBE_STATUS_IF_HEALTHCHECK **200**
- PLATFORM_WOULD_KILL_SINGLE_CONTAINER **False**
- READY_STATUS **503** READY_DATABASE disconnected (readiness still tells the truth)
- SHUTDOWN_HANDLER True GRACEFUL_SHUTDOWN_FLAG True
- CONTAINER_RUN not_run
