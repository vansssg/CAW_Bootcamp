# Production Readiness Module 06 FIX

BREAK B looked like a circuit that never heals. Code `reset_timeout` was already 30s; the gap was **observability of half-open trials**.

## Change
`BreakerLogger` now implements `before_call`, `failure`, and `success`:
- `circuit_before_call circuit_state=half-open` on a recovery trial
- `circuit_call_failed` with `error_type`
- `circuit_call_succeeded` after a healthy trial
- `circuit_open_fallback` includes `circuit_state`

An on-call can tell “still open, DB down” (`circuit_call_failed` + ConnectionTimeout) from “stuck open with no trials” (no `circuit_before_call` after 30s).

## Re-sim (probe breaker, fail_max=2, reset_timeout=1)
- `circuit_state_change` closed → open
- after 1.05s: `circuit_state_change` open → **half-open**
- `circuit_before_call circuit_state=half-open`
- `circuit_call_succeeded circuit_state=closed`
- `TRIAL ok`

Not claimed: live Postgres restart. A half-open trial against this laptop would fail and re-open — that is correct fail-closed, now visible in logs.
