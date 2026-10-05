# Runbook: /ready 200 but users failing (business path ≠ SELECT 1)

Linear checklist. Do not skip. Do not `docker rm`. This is the Module 08 BREAK case.

### Alert / Detection

- Alert name: `HighErrorRate` while `/ready` is 200, or user reports of 404 after restart / 500 on `/debug/error`
- Symptoms: dashboard green; `GET /r/{code}` 404 or 5xx; creates show `persisted=memory`
- Signal: `/ready` `checks.database=connected` AND a smoke `POST /links` + `GET /r/{code}` fails or `persisted` is not durable — not a dead process

### Diagnosis

**Step 1: `/live` vs `/ready` (dependencies only)**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; st,b=asyncio.run(asgi_request('/ready')); print(st, b.decode()[:300])"
```

- If this IS Postgres down: 503 `database: disconnected` — switch to `docs/runbooks/postgres-unreachable.md`
- If this is NOT: 200 with `checks.database=connected` — continue. Ready is not the user path.

**Step 2: Business smoke (not `/ready`)**

Use `python app/scripts/module08_deploy_smoke.py` from `api/`. Expect `POST /links` 200 and `GET /r/{code}` 307. If create is 200 `persisted=memory`, a restart will 404 those codes while `/ready` stays 200.

**Step 3: Config SHA**

`/ready` JSON `checks.image_sha` must match the compose/CI `IMAGE_TAG` / `GITHUB_SHA`. If `unknown`, this process was not started by `infra/deploy-local.sh` / the gated deploy job. Treat as config drift: do not edit `DATABASE_URL` in a UI; redeploy the tagged image.

**Step 4: Memory**

`checks.in_memory_links` and metric `urls_total`. Cap is `MAX_IN_MEMORY_LINKS=10000` (FIFO). If it sits at 10000, old codes 404 — that is eviction, not Postgres.

### Fix

1. Redeploy `IMAGE_TAG=<known git sha>` via `infra/deploy-local.sh` (Docker) or wait for CI `deploy` if `vars.DEPLOY_BASE_URL` is set.
2. Do not “fix forward” by changing compose `DATABASE_URL` in place without a new SHA.
3. `/debug/error` is 404 when `APP_ENV=production`.

### Verification

Re-run `app/scripts/module08_deploy_smoke.py`. `/live` 200. `/ready` must show `image_sha` not `unknown` after a tagged compose start. Business 307 still required.

### Escalation

15 minutes → `#linkops-alerts` with `/ready` body, `image_sha`, `persisted` from POST /links, timestamps.
