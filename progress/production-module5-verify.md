# Production Readiness Module 05 VERIFY

## Table checks
- Failure mode rows in `progress/production-module5-fmea.md`: **12** (8 required + network partition, DNS, pool exhaustion, clock skew).
- Simulations documented with actual command output: **2**.
- Desired handling differs from current on every request-path row (hang → 503+timeout; unused Redis → fail-open-if-introduced; OOM → memory limit+alert).

## Failure not thought of before
**Connection pool exhaustion.** Missed because "Postgres down" was treated as one mode. Module 04 hang showed workers can be stuck while Postgres is merely slow/unreachable, so the pool can empty with the database "up." DNS was the other late add: `DATABASE_URL` uses `localhost` here so hostname resolution never appeared in errors.

## Top 3 by risk (probability × impact)
1. **Postgres slow/hang (no timeout)** — high probability, full user freeze, **invisible to HighErrorRate** (no 5xx). Fix first: `connect_timeout` + fail-closed 503 on `/ready`, `/links`, `/r/{code}`.
2. **Postgres down at startup** — medium probability, process never serves `/metrics` (ServiceDown only if scraper exists). Same timeout fix unblocks startup vs infinite wait.
3. **Pool exhaustion** — follows (1); leftover hung connects occupy slots. `pool_timeout` after connect timeout.

## Analysis vs hoping
The table turns "add a feature" into "which dependency does this touch, timeout, fail-closed or open, transient vs permanent." Next feature (e.g. Redis cache for redirects) would get a row before code: fail-open to Postgres, TTL, never fail-open a wrong URL.

## Transient vs permanent
| Mode | Class | Retry? |
|---|---|---|
| Postgres restart connect timeout | Transient | Yes, bounded backoff |
| Postgres not running (this laptop) | Permanent until operator starts it | No tight retry loop |
| Missing table / schema | Permanent | No — fail fast + alert |
| Slow query / lock | Often transient | Retry can worsen; timeout then 504 |
| Bad JWT_SECRET / 401 | Permanent for that request | No |
| DNS blip | Transient | Yes, short backoff |
| Disk full / OOM | Permanent until ops | No app-level retry |

Red flag rejected: "the database won't go down" is false here — it is already down (`ConnectionTimeout` in 4.451s with `connect_timeout=1`).
