# Runbook: HighLatencyP95 (> 2s)

Linear checklist. Alert: `HighLatencyP95` in `progress/production-module4-alert-rules.yml`. Do not skip. Do not `docker rm`.

### Alert / Detection

- Alert name: `HighLatencyP95`
- Symptoms: pages feel stuck; p95 > 2s for 3 minutes
- Signal: histogram p95, or a single `/readyz` at ~4s (connect timeout), not “the site is slow”

### Diagnosis

**Step 1: Time `/live` (must be fast)**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,time,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; t=time.perf_counter(); st,b=asyncio.run(asgi_request('/live')); print(st, round(time.perf_counter()-t,3))"
```

- If this IS latency in the app process: `/live` also slow (well above 0.5s)
- If this is NOT: `/live` ~0.05s 200 — slowness is the DB path. Observed 2026-08-17: `200 0.052`

**Step 2: Time one `/readyz`**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,time,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; t=time.perf_counter(); st,b=asyncio.run(asgi_request('/readyz')); print('status',st,'secs',round(time.perf_counter()-t,3), b[:200])"
```

- If this IS Postgres connect timeout: `status 503 secs 4.0–4.5` — follow `docs/runbooks/postgres-unreachable.md`
- If breaker already open: `status 503 secs ~0.004` (fast fail — latency alert may drop)
- If healthy: status `200` under 1s
- Observed 2026-08-17: `READY1 503 4.082` then `READY2 503 4.073` — breaker still closed after two probes

**Step 3: Do not add retries**

Retries on `ConnectionTimeout` were rejected in Module 06 (4 × 4s). Do not “fix latency” by looping `/readyz`.

### Fix

**If Step 2 is ~4s 503:** follow `docs/runbooks/postgres-unreachable.md`. Do not restart the app for a connect timeout.

**If `/live` is slow and a named container exists:**

```bash
docker ps --filter name=url-shortener-prod --format "{{.Names}} {{.Status}}"
docker restart url-shortener-prod
```

- Expected: container restarts; `/live` returns 200 in under 0.5s
- If Docker daemon is down (`open //./pipe/dockerDesktopLinuxEngine`): **stop**. Escalate. Never `docker rm url-shortener-prod`.

### Verification

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,time,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; t=time.perf_counter(); st,b=asyncio.run(asgi_request('/live')); print('live',st, round(time.perf_counter()-t,3))"
```

- Expected: `live 200` under 0.5s

One `/readyz` only after that. Wait 2 minutes. Do not loop.

### Escalation

If not resolved in **15 minutes**:
1. Post in `#linkops-alerts`: `/live` seconds, `/readyz` status+seconds, whether you restarted `url-shortener-prod`, timestamps
2. Page primary on-call (Slack DM + phone)
3. If no response in 10 minutes, page secondary, then EM at 20 minutes
