# Production Readiness Module 06 REFLECT

## Decisions after BUILD/BREAK/FIX
Kept **A: pybreaker + aggressive 1s timeouts**. Would not switch to a custom breaker: the 5th `/ready` opened the circuit and the next five returned in **0.004s** — that half-open locking is what we would have gotten wrong. Would not switch to 5–10s conservative timeouts: first five requests already held ~4.1s each; 10s would be pool suicide. Would **not** add retries on `ConnectionTimeout` (CONTEXT math: 4 attempts × 4.1s).

## Q1 Timeouts, retries, breakers
Timeouts bound one call (`timeout_ms=1000`, still ~4.1s TCP). Retries are only for `ConnectionError`/`OSError` (delays 97ms, 189ms). Breaker watches **patterns**: `fail_max=5` then open. Together: one request worst-case ≈ one connect timeout, not `timeout*(retries+1)+backoff`. After open, cost is 4ms 503.

## Q2 PM version
If Postgres is sick, we stop waiting on it after a handful of failures. Users creating links get a fast “temporarily unavailable” instead of a spinner. We do not invent short URLs. `/live` still answers. When Postgres is healthy, a single trial request (`circuit_before_call half-open`) turns full service back on.

## Knowledge check
1. Core problem: fail-closed 503 still paid ~4s per request until a breaker opened.
2. Biggest decision: library breaker + no retries on ConnectionTimeout.
3. Evidence: timings `[4.131, 4.089, 4.078, 4.069, 4.08, 0.004, 0.004, 0.004, 0.004, 0.004]` plus half-open log `circuit_state=half-open` then `circuit_call_succeeded`.

## Mini practical
`module06_degradation_drill.py` 10× `/ready`; `FAST_AFTER_THRESHOLD_COUNT 5`.

## Risk + mitigation
Risk: after 30s the breaker half-opens and one trial again costs ~4s against a still-down DB.  
Mitigation: `circuit_before_call`/`circuit_call_failed` logs; runbook (M07) must not hammer `/ready`; do not retry 503 in the app.
