# Production Readiness Module 06 VERIFY

## 1) Timeouts on every external call
| Call | Where | Timeout |
|---|---|---|
| Postgres connect | `api/app/db.py` `connect_args.connect_timeout` | **1s** |
| Postgres statements | `options -c statement_timeout=1000` | **1000ms** |
| Pool wait | `pool_timeout` | **1s** |
| Redis | config only, no client in handlers | N/A |
| Outbound HTTP | none in `main.py` | N/A |

Library default of wait-forever is **not** accepted for Postgres. Remaining OS/TCP cost: ConnectionTimeout still ~4.1s in this environment after a 1s setting (driver retries); breaker then cuts further attempts to 4ms.

## 2) Circuit opens at threshold
Drill: 5 consecutive `/ready` failures then `circuit_state_change` to open. `fail_max=5` matches. 5th request still ~4.08s (that call is the one that trips); requests 6–10 are open-state.

## 3) Fallback is fast
`READY_5`–`READY_9` elapsed **0.004s** (4ms), body `{"detail":"service temporarily unavailable"}`. Fallback does not call Postgres (`circuit_open_fallback`).

## 4) Backoff + jitter
`retry_with_backoff` against ConnectionError: delays **0.0978s, 0.1899s** (`delay_ms=97`, `189`) — not exact 100/200. `RETRY_NOT_EXACT_POW2 True`.

## 5) Circuit closes after recovery
Live `docker start postgres` **not run** (no local Postgres). Probe breaker: after `reset_timeout=1`, trial `PROBE_TRIAL ok`, `PROBE_STATE_AFTER_SUCCESS closed`.

## Conceptual
1. Open breaker + new "purchase" analogue (`POST /links`): user sees **503** JSON, not a fake short code. Acceptable: a wrong redirect is worse than an error (DECIDE A / M05).
2. 5s vs 500ms: 100 rps * 5s = 500 held connections vs 50. This process already showed 4.1s holds until the breaker opened; after open, hold time is 4ms.

## Red flags checked
- Retries use backoff+jitter; ConnectionTimeout is not retried.
- Half-open exists (`reset_timeout=30` production breaker; probe closed after success).
- Fallback is in-process 503, not another DB query.
