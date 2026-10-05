# Production Readiness Module 06 BUILD

Decision A: **pybreaker** + **aggressive 1s** connect/statement timeouts. Fallback for Postgres is fail-closed **503**, never a guessed short URL.

## Chunk 1 — Timeouts
- `api/app/db.py`: `connect_timeout=1`, `pool_timeout=1`, `statement_timeout=1000ms`.
- Timeout log: `database unavailable` + `dependency=postgres` + `operation=ready` + `timeout_ms=1000`.
- Chosen vs P95: `/live` is 0.159s in-process; a healthy SELECT 1 should be tens of ms. 1s is >10x that and far below a 5–10s conservative hang. TCP still takes ~4.1s to surface ConnectionTimeout in this environment (driver/OS), then the breaker stops further connects.

## Chunk 2 — Circuit breaker
- `api/app/resilience.py`: pybreaker `fail_max=5`, `reset_timeout=30`, state-change logs.
- `call_postgres()` wraps lookup/create/ready/admin; analytics uses `fail_closed=False`.
- Open fallback: `circuit_open_fallback` + HTTP 503 (payment-like: do not invent a URL).

## Chunk 3 — Retry + jitter
- `retry_with_backoff`: exponential delay, jitter, only `ConnectionError`/`OSError`/`TimeoutError`.
- `OperationalError` / `CircuitBreakerError` are **not** retried (this laptop's missing Postgres is permanent; retries would 4x the 4s tax from CONTEXT).
- Helper proven: `RETRY_HELPER_CALLS 2` then `ok` after one `ConnectionError`.

## Failure-first drill
Command: `api/.venv/Scripts/python.exe app/scripts/module06_degradation_drill.py`

10x `GET /ready` with DB down:
- First 5: 503 in ~4.07–4.13s + timeout logs
- 5th failure: `circuit_state_change` closed → open
- Last 5: 503 in **0.004s** + `circuit_open_fallback` (no new DB connect)
- `FAST_AFTER_THRESHOLD_COUNT 5`

Half-open/close: probe breaker `fail_max=2`, `reset_timeout=1` → `PROBE_TRIAL ok`, `PROBE_STATE_AFTER_SUCCESS closed`.
**Not claimed:** `docker start postgres` recovery on this machine (Postgres not running; Docker previously unavailable).
