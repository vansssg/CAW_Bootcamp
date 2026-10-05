# Runbook: Postgres unreachable (connection timeout / breaker open)

Linear checklist. Do not skip. Do not `docker rm`.

### Alert / Detection

- Alert name: `HighErrorRate` (5xx / total > 5% for 2m) and/or operators seeing `/readyz` 503
- Symptoms: users cannot create links; `/live` still 200; readiness probe ~4s then 503 `service_unavailable`; logs `circuit_open_fallback` after 5 failures
- Signal: `/live` fast 200 AND readiness probe 503 with `postgres_connect_or_query_timeout` or breaker open — not a dead process. Current probe path is `/readyz` (was `/ready`; 404 means the path drifted).

### Diagnosis

**Step 1: Confirm the process is alive**

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,json,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; st,b=asyncio.run(asgi_request('/live')); print(st, b.decode())"
```

- If this IS the problem (DB down, process up): `200 {"ok":true}` in ~0.05s (logs also print `request completed path=/live status=200`)
- If this is NOT the problem (process dead): import error / hang — go to ServiceDown runbook

**Step 2: Time the readiness probe once (do not loop)**

Current path: `/readyz`. If this 404s, do Step 2b before treating it as Postgres.

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,time,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; t=time.perf_counter(); st,b=asyncio.run(asgi_request('/readyz')); print('status',st,'secs',round(time.perf_counter()-t,3), b[:200])"
```

- If this IS the problem (cold breaker): `status 503 secs 4.082` body `{"error":{"code":"service_unavailable","message":"service temporarily unavailable","request_id":"req-..."}}` plus log `failure_mode=postgres_connect_or_query_timeout`. A **second** probe is still ~4.07s until **five** failures open the breaker — do not expect 4ms after one probe.
- If this is NOT the problem: status `200` and secs well under `1`
- If this is PATH DRIFT: `status 404 secs 0.008` body `{"detail":"Not Found"}` — the process is up (`/live` 200) but this path is gone. Go to Step 2b. Observed 2026-08-17 when `/ready` was renamed to `/readyz`.

**Step 2b: If Step 2 was 404, find the current ready route**

```bash
cd api
.venv/Scripts/python.exe -c "from pathlib import Path; t=Path('app/main.py').read_text();
[print(i,l.rstrip()) for i,l in enumerate(t.splitlines(),1) if '@app.get(\"/ready' in l]"
```

- If this IS path drift: a line like `395 @app.get("/readyz")` and no `@app.get("/ready")`. Re-run Step 2 against the path that exists. Then update this runbook and `docs/service-overview.md` before closing the incident.
- If the print is empty: readiness was removed — escalate; do not guess a path.

**Step 3: Is Postgres listening?**

```bash
docker ps --filter name=linkops-postgres --format "{{.Names}} {{.Status}}"
```

- If this IS the problem: Docker daemon down. Observed 2026-08-17: `error during connect: ... open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`
- If this is NOT the problem: `linkops-postgres Up ... (healthy)`

**Step 4: TCP 5432**

```bash
python -c "import socket; s=socket.create_connection(('127.0.0.1',5432),1); print('open'); s.close()"
```

- If this IS the problem: `TimeoutError timed out` (observed on this host) or `ConnectionRefusedError`
- If this is NOT the problem: prints `open`

### Fix

**Step 1: Start Postgres only if Docker works**

```bash
cd infra
docker compose up -d postgres
```

- Expected: container `linkops-postgres` starts
- If Docker daemon is down: **stop**. You cannot start Postgres from this runbook. Escalate. Do not invent a start.

**Step 2: Do not hammer `/readyz`**

Wait 30s for `reset_timeout` (hardcoded in `api/app/resilience.py`). One trial request only.

### Verification

```bash
cd api
.venv/Scripts/python.exe -c "import asyncio,sys; sys.path.insert(0,'.'); from app.scripts.module06_degradation_drill import asgi_request; st,b=asyncio.run(asgi_request('/live')); print('live',st)"
```

- Expected: `live 200`

If Postgres actually started, one `/readyz` should 200. If Postgres did not start, `/readyz` stays 503 — that is honest, not a failed runbook.

Wait 2 minutes: do **not** send 10 `/readyz` probes (opens breaker and burns 4s×5).

### Escalation

If not resolved in **15 minutes**:
1. Post in `#linkops-alerts`: `/live` status, `/readyz` status+seconds (or 404 if path drifted), `docker ps` output, timestamps
2. Page primary on-call (Slack DM + phone)
3. If no response in 10 minutes, page secondary, then EM at 20 minutes
