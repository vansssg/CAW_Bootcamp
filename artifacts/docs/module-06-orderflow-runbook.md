# OrderFlow On-Call Runbook (3 AM)

**Service:** OrderFlow — checkout → ship path (create order, status, pay, refund)  
**Docs strategy:** Minimal in-repo (this runbook + README); diagrams/API OpenAPI linked out  
**Prereqs (install once on laptop):** `kubectl`, `helm`, `curl`, `redis-cli`, `psql` must be on PATH. Check: `kubectl version --client`, `helm version`, `which redis-cli`, `psql --version`. If missing, use company laptop bootstrap doc (link: Notion → “Dev laptop setup”) — do not invent install paths at 3 AM; escalate to `#platform-infra` if bootstrap fails.

**Canonical values (edit once):**

| Name | Value |
|------|-------|
| API port | `8080` |
| Health URL | `http://localhost:8080/health` (local) / `https://orderflow.internal.company.com/health` (prod) |
| Namespace | `production` |
| Helm release | `orderflow` |
| Slack on-call | `#orderflow-oncall` |
| PagerDuty | Escalation policy **OrderFlow Primary** |
| Data eng | `#data-eng` |
| Infra | `#platform-infra` |

**Constraints twist (M05):** Keep steps plain; lead recovery with customer impact (“checkout failing”) not jargon.

---

## 0. Are we on fire? (30 seconds)

1. Open PagerDuty alert → note **symptom** (5xx / latency / refund lag / DB).  
2. Slack `#orderflow-oncall`: “Acked. Investigating OrderFlow — [symptom].”  
3. Go to **§1 Health check**.

---

## 1. Health check (copy-paste)

```bash
curl -sS -o /tmp/of-health.json -w "%{http_code}" https://orderflow.internal.company.com/health
echo
cat /tmp/of-health.json
```

**Healthy looks like:** HTTP `200` and JSON includes `"status":"ok"` (or equivalent) plus DB/Redis flags green if present.

**Unhealthy symptoms for this service:**

| Symptom | Meaning |
|---------|---------|
| HTTP 5xx on `/health` or checkout | API process/config/deps broken |
| `/health` 200 but **orders not creating** | Silent app bug or DB write failure (don’t trust HTTP alone) |
| Checkout OK, refunds stuck | **Celery worker** down or broker issue |
| Slow status reads, rate limits off | **Redis** down (API degrades, still up) |

**Decision:**  
- If API unreachable or 5xx → **§2 API 5xx**  
- If API up, refunds not completing → **§3 Worker**  
- If DB errors in logs → **§4 Database**  
- If bad deploy suspected → **§5 Rollback**  
- If stuck >15 min or data loss risk → **§6 Escalate**

---

## 2. API returning 5xx

1. Check pods:
```bash
kubectl -n production get pods -l app=orderflow
kubectl -n production describe pod -l app=orderflow | tail -n 80
```
2. Logs (last 10 min):
```bash
kubectl -n production logs -l app=orderflow --since=10m --tail=200
```
3. Confirm env present (do **not** print secrets):
```bash
kubectl -n production get deploy orderflow -o jsonpath='{.spec.template.spec.containers[0].env[*].name}{"\n"}'
```
Expect names: `DATABASE_URL`, `REDIS_URL`, `AUTH_SERVICE_URL`, `STRIPE_API_KEY`, `SENTRY_DSN`, `PORT`, `CELERY_BROKER_URL`, `LOG_LEVEL`.

4. **If** crashloop / bad image → **§5 Rollback**  
5. **If** auth errors to auth service → page owner of `AUTH_SERVICE_URL` via `#platform-infra`  
6. Re-check §1. If still red after 10 min → **§6 Escalate**

---

## 3. Refunds queued but not processing (worker)

1. Confirm queue depth (Redis DB 1 broker):
```bash
redis-cli -u "$REDIS_URL" PING
# If using CELERY_BROKER_URL redis://.../1:
redis-cli -u "${CELERY_BROKER_URL:-redis://localhost:6379/1}" LLEN celery
```
2. Worker process / pods:
```bash
kubectl -n production get pods -l app=orderflow-worker
kubectl -n production logs -l app=orderflow-worker --since=30m --tail=200
```
3. Restart worker (if safe):
```bash
kubectl -n production rollout restart deploy/orderflow-worker
kubectl -n production rollout status deploy/orderflow-worker
```
4. **If** Redis down: API may still serve; refunds + rate limits impaired → fix Redis with `#platform-infra`, then restart worker.  
5. Re-test: request a **staging** refund or watch queue length drop.  
6. Still stuck → **§6 Escalate**

---

## 4. Database connection lost

1. From a jump host / with prod credentials configured:
```bash
psql "$DATABASE_URL" -c 'SELECT 1;'
```
2. **If** connection fails → `#data-eng` + `#platform-infra` immediately (do not “fix” Postgres alone at 3 AM unless you own it).  
3. API logs for `OperationalError` / connection refused:
```bash
kubectl -n production logs -l app=orderflow --since=15m | grep -i -E 'operationalerror|connection|timeout|psycopg'
```
4. **If** DB up but migrations missing (fresh env only — **not** typical prod firefight):
```bash
alembic upgrade head
```
5. Re-check §1.

---

## 5. Rollback bad deploy

1. See revisions:
```bash
helm history orderflow --namespace production
```
2. Rollback one revision:
```bash
helm rollback orderflow --namespace production
```
3. Wait:
```bash
kubectl -n production rollout status deploy/orderflow
```
4. Re-run §1 health + one synthetic checkout (or ask canary).  
5. **If** rollback command errors (stale chart path) → **§6 Escalate** to `#platform-infra` (do not invent paths).

---

## 6. Escalate

| When | Who | How |
|------|-----|-----|
| >15 min no progress | Next on OrderFlow Primary | PagerDuty **escalate** |
| DB / data integrity | `#data-eng` | Slack + PD if Sev-1 |
| Cluster / Helm / Redis platform | `#platform-infra` | Slack + PD |
| Suspected payment double-charge | Platform Payments owner + Security | PD + `#orderflow-oncall` |

Message template:
`OrderFlow Sev-X: [symptom]. Health=[code]. Steps tried: [§]. Need: [DB|Helm|Redis|Auth].`

---

## 7. After stabilize

1. Note timeline in `#orderflow-oncall`.  
2. Open follow-up ticket: stale runbook / missing alert / bad deploy.  
3. If customer orders/refunds impacted → start blameless postmortem draft (link Module 04 template).

---

## Do not

- Paste live `STRIPE_API_KEY` / DB passwords into Slack.  
- Follow outdated “use pg_dump” notes if deploy dir says Helm/LVM — **trust this file + `deploy/`**, then escalate if mismatch (GitLab lesson).
