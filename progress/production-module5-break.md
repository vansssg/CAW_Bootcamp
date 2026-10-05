# Production Readiness Module 05 BREAK

No new Postgres hang experiment. Diagnosis uses Module 04 BREAK `/ready` timeout, Module 05 sim2 (`connect_timeout=1` → `ConnectionTimeout` in 4.451s), ASGI `/live` 200, and current `api/app/main.py` / `api/app/db.py`.

## Symptom (what an on-call sees)
- `GET /live` returns **200** `{"ok":true}` (`req-dd6dfc2d`).
- User-facing create/redirect/`/ready` do **not** complete: default `engine.connect()` occupied the BREAK process until `/ready` hit `S1_READY_STATUS TIMEOUT` with `S1_READY_HANG_NO_500_NO_METRIC_COMPLETION True`.
- Module 04 HighErrorRate cannot page this: **no completed 5xx**, so `http_requests_total{status="5xx"}` stays flat while workers are stuck.
- `/metrics` is in-process; if the worker is blocked on connect, scrape is also at risk (Facebook-shaped coupling).

This is **Option B (slow/unreachable dependency, not a clean crash)** plus a hidden **Option C (partial failure)** on the redirect path.

## Root cause (not “Postgres is down” as a single mode)
`api/app/db.py` is `create_engine(DATABASE_URL, future=True)` — **no** `connect_timeout`, **no** `pool_timeout`, **no** `statement_timeout`. Sync handlers call `engine.connect()` / `engine.begin()` on the request thread. When the TCP handshake never finishes, the request never becomes a 503, never logs `level=error` for that request, and never increments the error counter.

Sim2 already proved the library *can* fail fast: a cloned engine with `connect_args={"connect_timeout": 1}` raised `OperationalError` / `psycopg.errors.ConnectionTimeout` in **4.451s**. Production engine does not use that setting. Gap is configuration + fail-closed mapping, not “we need another hang trace.”

## Missed mode: partial failure (reads vs writes)
The FMEA listed down/slow/pool but not **read-only primary / replica failover**.

| Path | User intent | SQL | If DB is read-only |
|---|---|---|---|
| `GET /live` | liveness | none | 200 |
| `GET /ready` | readiness | `SELECT 1` | 200 — monitoring says up |
| `GET /r/{code}` | “just open the link” | `SELECT` **then `INSERT analytics`** | **write fails** after a successful lookup |
| `POST /links` | create | `INSERT` | fails |

`GET /r/{code}` is a browse/read in product terms and a **write** in SQL. A read-replica or `default_transaction_read_only` outage looks like “site is up, shortening/redirects randomly fail.” `/ready` would still pass. That is why `/live` + `/ready` as currently written cannot detect Option C.

## Highest-risk failure mode (fix first)
**Unbounded Postgres connect/query wait (slow or down, no timeout).**

Risk = high probability (this environment already exhibits it) × impact (all data paths freeze) × **detection miss** (no 5xx → HighErrorRate silent; `/live` green).

Pool exhaustion is a downstream effect of the same hang, not a separate first fix.

Partial-failure on `/r/{code}` is the second fix in the same change: do not couple redirect success to analytics insert.

## What FIX must change (implemented vs still planned)
Implemented in FIX (this module):
1. Production engine: `connect_timeout`, `pool_timeout`, statement timeout.
2. Fail-closed **503** on `/ready`, `POST /links`, admin DB paths when `OperationalError`/timeout fires; log `error` + `request_id`.
3. Startup DB check must **not** block process boot forever (keep `/live` + `/metrics` up — DECIDE A refinement + Module 04 interlude).
4. `GET /r/{code}`: fail-closed 503 if the **lookup** fails; if analytics `INSERT` fails, still redirect and `warn` (fail-open on telemetry only, never invent a URL).

Not claimed: live Docker DNS `/etc/hosts` override; live read-only Postgres; Prometheus `for: 2m` firing.
