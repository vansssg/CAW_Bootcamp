# Production Readiness Module 05 — Failure Mode Analysis

Default stance (DECIDE A): **fail-closed** on Postgres-backed read/write/redirect. `/live` stays independent.

## Chunk 1 — Dependency inventory

| Dependency | Connection method | Configured timeout | Retry behavior |
|---|---|---|---|
| Postgres | SQLAlchemy `create_engine(DATABASE_URL)` + psycopg TCP (`api/app/db.py`) | **None** (library default; connect hung >30s in Module 04) | None in app code |
| Redis | `REDIS_URL` required by `api/app/config.py` only | N/A on request path (no Redis client calls in handlers) | N/A |
| External HTTP APIs | None in `api/app/main.py` | N/A | N/A |
| File system | Stdlib logging StreamHandler to stdout (no log file path) | N/A | None |
| DNS | OS resolver for host in `DATABASE_URL` / `REDIS_URL` | OS/resolver default | OS retry |
| Runtime (CPU/memory) | Single uvicorn/FastAPI process | N/A | Container restart only if orchestrator exists |
| Prometheus scraper | Pull `GET /metrics` | Scrape timeout is on the scraper, not this app | Alert `ServiceDown` if scraper exists |

Timeout column: **0 of the used request-path dependencies have an explicit timeout in code.** Postgres is the live risk (`?` → proven hang).

DNS note: current `.env` uses `localhost`, so this environment skips remote DNS. A hostname-based `DATABASE_URL` would fail with host-not-found / timeout, not a clear "DNS" log line.

## Chunk 2 — Failure mode table

| Dependency | Failure mode | Probability | User impact | Current handling | Desired handling |
|---|---|---|---|---|---|
| Postgres | Connection refused / process down | Medium | Redirects and creates fail; process may never finish startup | Hang on `engine.connect()` / startup `SELECT 1`; `/live` 200 only if lifespan skipped | Fail-closed 503 after connect timeout; keep `/live` 200; log error + `request_id` |
| Postgres | Slow queries / slow connect | High | Workers drain; `/metrics` can stall | No statement/connect timeout; Module 04 `/ready` blocked the event loop | Connect+query timeout, 504, slow-query log, pool timeout |
| Redis | Down | Medium | None today (unused on path) | Config still requires `REDIS_URL` at import | If later used: fail-open to Postgres with warn log |
| Redis | Stale cache | High if introduced | Wrong redirect if cache used for codes | Not applicable (no cache-aside) | TTL + never cache redirects longer than link updates |
| External API | Down | Low (none called) | N/A | N/A | Circuit breaker if one is added |
| External API | Slow | Low | N/A | N/A | Strict timeout |
| Disk | Full | Low-Medium | Container logging may fail; stdout still used | No disk gauge/alert in-app | Log rotation at runtime; disk usage alert |
| Runtime | OOM | Low-Medium | Process killed; in-flight requests lost | `urls_total` gauge only; no heap alert | Memory limit + 80% alert |
| Network | Partition (DB unreachable, process up) | Medium | Same as Postgres down for data paths | Hang | Same as connect timeout 503 |
| DNS | Hostname does not resolve | Medium in cloud | Cryptic connect errors | Unhandled | Bounded resolver timeout, explicit error log |
| Postgres pool | Pool exhaustion from hung queries | High once traffic exists | New requests wait forever | Default pool, no timeout | `pool_timeout` + fail-closed 503 |
| Postgres | Partial failure: reads succeed, writes fail (read replica / `default_transaction_read_only`) | Medium (failover, cloud replica) | `/live` and `/ready` (SELECT 1) stay 200; `POST /links` fails; `GET /r/{code}` fails on analytics INSERT even though lookup is a user “read” | **Observed in BREAK (code + /live 200 vs hung writes):** redirect and create share write coupling; `/ready` cannot see Option C | Fail-closed 503 on lookup/create timeout; decouple analytics INSERT from redirect (warn + still redirect); never invent a URL |
| Clock | Skew | Low | Admin token compare is raw `JWT_SECRET`, not expiring JWT — skew is limited today | No clock check | If real JWTs added: NTP + leeway |

**Current-handling risk surface (hang / crash / unhandled):** Postgres down, Postgres slow, pool exhaustion, DNS, disk, OOM = **6**. Redis unused so not counted as a request-path crash.

## Chunk 3 — Simulations (real, not imagined)

### Simulation 1 — Database already stopped

Did **not** run `docker stop postgres`: Docker daemon was previously unavailable, and nothing is listening on `localhost:5432`. That is the stopped-database state.

| Check | Result |
|---|---|
| User `/live` (ASGI, no lifespan) | HTTP **200** `{"ok":true}` `request_id=req-dd6dfc2d` |
| User `/ready` or `engine.connect()` default | **Hang** (Module 04: killed after ~30s, no SELECT 1; BREAK script stuck on GET /ready) |
| Logs | `/live` info completed; hung connect produced **no** error log and **no** completed 500 metric |
| Time until notice | HighErrorRate does not fire (no 5xx). ServiceDown only if an external scraper exists (none running). Operators notice via hang/timeout, not an alert |

Vs table: Current handling said hang — **confirmed**. Gap: no connect timeout, no 503, no error log, no metric.

### Simulation 2 — Impossibly low DB connect timeout

Command: `api/.venv/Scripts/python.exe app/scripts/module05_timeout_sim.py`  
Engine clone with `connect_args={"connect_timeout": 1}` (psycopg timeout is seconds; 1ms is not a valid psycopg unit).

| Check | Result |
|---|---|
| Result | `OperationalError` / `psycopg.errors.ConnectionTimeout` `connection timeout expired` |
| Elapsed | **4.451s** (not infinite hang) |
| Logs | Exception at client; production handlers still do not catch this on `/ready` because that path has no timeout today |
| Notice | Fail-fast enough to log and count 503 **if** wired into `/ready` and `/links`; **not wired yet** |

| Simulation | Expected | Actual | Gap |
|---|---|---|---|
| Database stopped | Fast 503 on data paths; `/live` 200 | `/live` 200; data/startup **hang** | No timeout; no fail-closed 503 |
| 1s connect timeout | Fail fast | `ConnectionTimeout` in 4.451s on a **test engine only** | Production `create_engine` still has no `connect_timeout` |

Implemented vs planned: FMEA + simulations **done**. Production fail-closed timeout on `api/app/db.py` is **planned for FIX**, not claimed as shipped.
