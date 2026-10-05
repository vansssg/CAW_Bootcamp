# Production Readiness Module 05 REFLECT

## 1) Fail-closed vs fail-open after simulation
Default stance **A fail-closed** still holds for **source-of-truth** paths: `POST /links` and redirect **lookup**. A guessed URL is worse than 503.

It now **varies by dependency/path**:
- Postgres lookup/create/admin: **fail-closed 503** (DECIDE A).
- `/live` + `/metrics`: **independent of Postgres** (process can boot after a timed startup check).
- Analytics INSERT on `GET /r/{code}`: **fail-open** (warn + still redirect) because dropping click counts is better than blocking a known-good destination.
- Redis: unused on the request path; if added later, fail-open to Postgres, never fail-open a cached wrong URL.

Fail-closed was **fail-opaque** before FIX: hang produced no 503, so the stance could not fire. Detection (`connect_timeout` → `ConnectionTimeout` → named log) is what made fail-closed real.

## 2) Simulation surprise
Expected “DB down” → fast error. Actual before FIX: `/live` 200 and `/ready` **TIMEOUT with no 5xx**. After FIX, same environment: `/ready` **503 in 4.271s** with `failure_mode=postgres_connect_or_query_timeout`. The surprise was not that Postgres was unreachable — it was that **liveness hid the outage from HighErrorRate**.

## 3) If only one mode to protect
**Unbounded connect/query wait.** It is high probability here, freezes every data path, and was invisible to the Module 04 error-rate alert. Pool exhaustion and “startup never serves /metrics” are the same class. Option C (read-only replica) matters, but only after requests complete at all.

## Knowledge check
1. Core problem: enumerate how this shortener actually fails (hang vs 5xx vs partial write) before the 3 AM page.
2. Biggest decision: fail-closed on URL truth, plus timeouts so “down/slow” is detectable — without that, DECIDE A is a comment in a doc.
3. Evidence: `module05_failure_fix_verify.py` → `/live` 200; `/ready` 503 4.271s; `POST /links` 503; `/r/abc123` 503; log `database unavailable` + `action=ready` + `ConnectionTimeout`.

## Mini practical
Command: `api/.venv/Scripts/python.exe app/scripts/module05_failure_fix_verify.py`  
`FIX_READY_STATUS 503` `FIX_READY_ELAPSED_S 4.271` `FIX_CREATE_BODY {"detail":"service temporarily unavailable"}` `FIX_LOG_HAS_FAILURE_MODE True`.

## Risk + mitigation
Risk: clients retry 503 forever against a **permanent** local-down (this laptop has no Postgres).  
Mitigation: no app-level retry on 503; log `failure_mode` for operators; treat missing-server as permanent, restart-timeout as transient (Module 06 backoff/circuit breaker).
