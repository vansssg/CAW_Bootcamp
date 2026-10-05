# Service overview (operator pager manual)

## Purpose

URL shortener API: authenticated clients create owner-scoped short codes; anyone hitting `GET /r/{code}` gets a 307 to the long URL. Click analytics, cache, and jobs are side paths — the pager cares that redirects stay 307 and writes fail closed when Postgres is sick.

## Dependencies

| Dependency | Type | What happens without it | Fallback (Module 06) |
|---|---|---|---|
| PostgreSQL `localhost:5432` (compose name `linkops-postgres`) | Primary datastore for durable links | Creates and `/readyz` fail-closed 503 after connect timeout + breaker | No fake URLs. In this workspace create/redirect SoT can be in-memory when DB is down (`persisted=memory`). `/live` stays 200. |
| Redis `localhost:6379` (`linkops-redis`) | Cache / job broker (intended) | Redirects still work | `api/app/cache.py` pings with 0.2s timeout then in-process TTL map. Jobs use in-process `queue.Queue`, not Celery. |
| External geocoding API | None in this service | N/A | N/A |
| Docker daemon | Runtime for compose | Cannot start/stop `linkops-postgres` | Diagnose with ASGI `/live` `/readyz`; do not invent `docker start` success. |

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/live` | Liveness: process up, no DB |
| GET | `/ready` and `/readyz` | Same handler: `SELECT 1` + cache ping report + `uptime_seconds`. 200 only if database connected. `/readyz` kept so the Module 07 path-drift clients still work. |
| GET | `/metrics` | Prometheus text |
| GET | `/debug/error` | Deliberate 500 for drills |
| POST | `/links` | Create short code (`X-API-Key`) |
| GET | `/r/{code}` | Public 307 redirect |
| GET | `/links/{code}` | Owner analytics metadata |
| PATCH | `/links/{code}` | Update long URL; invalidates cache |
| DELETE | `/links/{code}` | Delete mapping |
| GET | `/links/{code}/analytics` | Owner click series |
| POST | `/api/admin/purge-clicks` | Retention purge |

## Configuration

Source of truth: `api/.env.example`. **Restart required** for all of these (Pydantic Settings load at import). None are hot-reload.

| Variable | Safe to change at 3 AM? | Effect |
|---|---|---|
| `LOG_LEVEL` | Yes after restart | `debug\|info\|warn\|error` |
| `PORT` | Only with matching healthcheck | Default in image **3000** |
| `DATABASE_URL` | No without a rollback plan | Must not be localhost when `APP_ENV=production` |
| `REDIS_URL` | Same | Required at boot even if Redis is down at runtime |
| `JWT_SECRET` | No | Auth signing; ≥32 chars; not an API key |
| `API_KEY_A` / `API_KEY_B` | No | Distinct ≥32-char keys |
| `APP_ENV` | No | `production` rejects localhost URLs |
| `CORS_ORIGIN` | Low risk | CORS allowlist |

**Not env vars — code constants (need a deploy to change):**

- `DB_CONNECT_TIMEOUT_S = 1` and `statement_timeout=1000ms` in `api/app/db.py`
- Circuit breaker `fail_max=5`, `reset_timeout=30` in `api/app/resilience.py`

## Deploy (exact)

There is **no Railway** in this repo. Production deploy path that exists:

```bash
git push origin main
```

CI (`.github/workflows/ci.yml`) runs ruff + `python app/scripts/test_query_columns.py` on `api/`. It does **not** SSH to a host.

Local/compose (only if Docker daemon is up):

```bash
cd infra
docker compose up -d postgres redis
cd ../api
docker build -t url-shortener:local .
docker run --rm -p 3000:3000 --env-file .env --name url-shortener-prod url-shortener:local
```

Verify (replace host if you have one; local expected):

```bash
curl -sS -m 2 http://127.0.0.1:3000/live
curl -sS -m 5 http://127.0.0.1:3000/readyz
```

Expected when DB is up: `/live` `{"ok":true}` 200; `/readyz` 200 with a DB check. Expected in **this workspace today**: `/live` 200; `/readyz` 503 after ~4s then fast 503 once the breaker opens. A 404 on `/ready` means the probe path drifted (Module 07 BREAK). Do not claim compose is up unless `docker ps` shows `linkops-postgres`.

## Rollback (exact)

No `railway rollback`. Previous version is the previous git SHA / image tag:

```bash
git log -2 --oneline
git revert --no-edit HEAD
git push origin main
```

If you ran a local container:

```bash
docker stop url-shortener-prod
docker run --rm -p 3000:3000 --env-file .env --name url-shortener-prod url-shortener:<previous-tag>
```

Verify with the same two curls as Deploy.

## Ownership

| Role | Who | Channel | Escalate if silent |
|---|---|---|---|
| Service owner | URL-shortener bootcamp team | `#linkops-alerts` | 15 minutes |
| Primary on-call | The engineer holding the pager | Slack DM + phone | 10 minutes |
| Secondary on-call | Backup on-call | Phone | 10 minutes after primary |
| Engineering manager | EM on-call | Phone | 20 minutes total |

Do not debug alone past **15 minutes** at 3 AM.
