# Runbook: HighErrorRate (5xx > 5%)

Linear checklist. Alert: `HighErrorRate` in `progress/production-module4-alert-rules.yml`. Do not skip. Do not `docker rm`.

### Alert / Detection

- Alert name: `HighErrorRate`
- Symptoms: clients see 5xx; Prometheus `http_requests_total{status=~"5.."}` elevated
- Signal: 5xx rate / total > 0.05 for 2 minutes — not a single 500

### Diagnosis

**Step 1: Confirm the process is alive**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,json,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; st,b=asyncio.run(asgi_request('/live')); print(st, b.decode())"
```

- If this IS a dead process: import error / hang — ServiceDown, not this runbook
- If this is NOT: `200 {"ok":true}` in ~0.05s — continue

**Step 2: Time `/readyz` once**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,time,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; t=time.perf_counter(); st,b=asyncio.run(asgi_request('/readyz')); print('status',st,'secs',round(time.perf_counter()-t,3), b[:200])"
```

- If this IS dependency/breaker: `status 503 secs 4.0–4.5` body `error.code=service_unavailable` — **stop this runbook** and follow `docs/runbooks/postgres-unreachable.md`
- If this is NOT: status `200` and secs well under `1` — continue
- If 404 `{"detail":"Not Found"}`: path drift — postgres-unreachable Step 2b
- Observed 2026-08-17 with Docker down: `/readyz` `503 4.087`; old `/ready` was `404 0.008`

**Step 3: Confirm 5xx are not all `/readyz`**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; st,b=asyncio.run(asgi_request('/r/no-such-code')); print('redirect_probe',st, (b[:120] if b else None))"
```

- If this IS Postgres-only 5xx: `/r/{code}` is 404 JSON or 307, while `/readyz` is 503 — treat as Postgres, not app crash
- If this IS app crash: `/r/{code}` also 5xx with `internal_error`

**Step 4: Hit the drill 500 (only if you intend to confirm error envelope)**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; st,b=asyncio.run(asgi_request('/debug/error')); print(st, b[:300])"
```

- If handlers work: `500` JSON `internal_error` with `request_id`
- If this is NOT the production incident: you just created one 500 — stop using `/debug/error` on prod

### Fix

**Step 1: If Step 2 was 503 ~4s**

Follow `docs/runbooks/postgres-unreachable.md` from Diagnosis Step 3 (docker ps). Do not restart the app for a DB timeout.

**Step 2: If a bad deploy (both `/live` and `/r/{code}` 5xx after a push)**

```bash
git log -2 --oneline
git revert --no-edit HEAD
git push origin main
```

Expected: revert commit on `origin/main`. There is no Railway rollback.

If a local container is running:

```bash
docker stop url-shortener-prod
docker run --rm -p 3000:3000 --env-file .env --name url-shortener-prod url-shortener:<previous-tag>
```

- If Docker daemon is down: **stop**. Escalate. Do not `docker rm url-shortener-prod`.

### Verification

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; st,b=asyncio.run(asgi_request('/live')); print('live',st)"
```

- Expected: `live 200`

If Postgres is actually up, one `/readyz` should 200. If it is not, `/readyz` stays 503 — that is the Postgres runbook, not a failed HighErrorRate close.

Wait 2 minutes. Do not loop `/readyz`.

### Escalation

If not resolved in **15 minutes**:
1. Post in `#linkops-alerts`: `/live` status, `/readyz` status+seconds, whether `/r/{code}` is 5xx, timestamps
2. Page primary on-call (Slack DM + phone)
3. If no response in 10 minutes, page secondary, then EM at 20 minutes
