# Module 04 VERIFY Evidence

## Bug #6 (memory leak) - Available evidence

### Commands and observed outputs
- Service startup command:
  - `./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 3000`
  - Observed: `Started server process` then `Waiting for application startup.` (no readiness completion).
- Health probe:
  - `curl -sS -m 5 http://127.0.0.1:3000/health`
  - Observed: connection failure to port 3000.
- DB connectivity check:
  - SQLAlchemy `SELECT 1` one-liner through project DB URL.
  - Observed: command remained waiting; no successful DB response.
- Port inspection:
  - `netstat -an | rg "5432|6379|3000"`
  - Observed: no listening entries for expected runtime dependencies.

### Verification conclusion for Bug #6
- Required memory-profile verification (start/end memory after 2,000 requests) could not be produced because service dependencies were unavailable and app did not become request-ready.

### finally-block reasoning (non-fabricated conceptual explanation)
- If resource release is only in success branch, any error path skips release and leaked resources accumulate.
- Moving release to `finally` guarantees execution on both success and error paths, preventing leak growth from error traffic.
- This module run did not include a successful live repro to numerically prove memory delta due the runtime blocker above.

## Bug #7 (N+1 query) - Available evidence

### Commands and observed outputs
- Query-log before/after comparisons were not obtainable because runtime never reached a request-ready state and DB was unreachable.
- `/links` response-time check for 50 rows was not executable for same reason.

### Verification conclusion for Bug #7
- Required query-count proof (e.g., 51 queries before, 1-2 after) and latency proof (<200ms) are unavailable in this execution environment.

## Limitation (explicit)
- Evidence unavailable due local runtime dependency unavailability (no reachable Postgres/Redis/API startup completion at execution time).
- No profiler snapshots, heap comparisons, or DB query logs were fabricated.
