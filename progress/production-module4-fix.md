# Production Readiness Module 04 FIX

## Changes in `api/app/main.py`
1. Silent 5xx: keep middleware `except Exception` logging `level=error` with `stack_trace` and HTTP 500. `/debug/error` still raises `RuntimeError` so logs are not swallowed.
2. Cardinality: `metric_path()` labels with the FastAPI route template (`/debug/error`, `/r/{code}`) or `/unmatched` for unknown URLs. Raw `request.url.path` is no longer a metric label.
3. Request ID: `REQUEST_ID_CTX` contextvar is set in middleware; `emit_log()` inherits it when callers omit `request_id` (e.g. `link created`).

Not implemented (planned, not claimed): query timeouts on `/ready`/`engine.connect()`. That hang is an environment/DB blocker, not a swallowed handler.

## Post-fix command
`api/.venv/Scripts/python.exe app/scripts/module04_observability_fix.py`

Observed:
- `FIX_GHOST_RAW_PATH_SERIES []`
- `FIX_UNMATCHED_SERIES [('/unmatched', '404', 12.0)]`
- `FIX_CARDINALITY_COLLAPSED True`
- `FIX_DEBUG_ERROR_STATUS 500` / `FIX_DEBUG_ERROR_REQUEST_ID req-fix-500`
- `FIX_DEBUG_500_METRIC [('/debug/error', '500', 1.0)]`
- `FIX_ERROR_LOG_HAS_STACK True`
- `FIX_ERROR_LOG_HAS_REQUEST_ID True`
- `FIX_INNER_LOG_INHERITS_REQUEST_ID True` (`request_id=req-fix-inner` on `link created`)

## Three pillars after error
1. Logs: `ERROR unhandled exception ... request_id=req-fix-500 ... RuntimeError: forced observability test error`
2. Metrics: `http_requests_total{path="/debug/error",status="500"} 1.0`
3. Alerts: process snapshot error rate `1/14 ≈ 0.071 > 0.05`, so HighErrorRate **expression** would be true. Not claimed: Prometheus `for: 2m` evaluation against a live scraper (no running uvicorn/Prometheus).
