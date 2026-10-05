# Production Readiness Module 06 BREAK

Inspected the three injected-failure classes against `api/app/resilience.py` and the drill output. No new Postgres hang.

## Failure A — runaway retry
**Disproved in code.** `retry_with_backoff` loops `range(max_retries + 1)` and breaks; default `max_retries=2`. HTTP path does not call it for `OperationalError` (re-raised). A single `/ready` produced one timeout log, not hundreds. CPU spike from infinite retries is not this process.

## Failure C — synchronized stampede
**Disproved in measurement.** Jitter is `random.uniform(-jitter, jitter)` on the exponential delay. Captured delays **0.0978s, 0.1899s** (`delay_ms=97`, `189`), not 100/200/400. `RETRY_NOT_EXACT_POW2 True`.

## Failure B — circuit that never heals
**Symptom matches operations, not a broken `reset_timeout`.**
- Code: `reset_timeout=30`, not 999999.
- Probe breaker with a succeeding trial: `PROBE_TRIAL ok`, `PROBE_STATE_AFTER_SUCCESS closed`.
- This environment never restarted Postgres, so a half-open trial would call `engine.connect()`, get `ConnectionTimeout` again, and **correctly re-open**. That looks like “never heals” from the dashboard (`circuit_open_fallback` forever) while the dependency is still dead.

Root cause to carry into FIX: on-call cannot tell **open because DB is down** from **open because half-open is stuck**. Logs currently say `circuit_open_fallback` without `circuit_state` / trial outcome. Probe showed `PROBE_STATE_AFTER_WAIT open` even after `reset_timeout` — pybreaker applies half-open on the *next call*, which we should log.

## Highest-risk remaining gap
Open-state 503 is fast (4ms) — good. Recovery observability is weak. FIX: log `circuit_state` and whether a call is a half-open trial, without inventing a URL fallback.
