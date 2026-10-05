# Production Readiness Module 04 BREAK

Hypothesis-first diagnosis of the three observability failure classes against the running code. Command: `api/.venv/Scripts/python.exe app/scripts/module04_observability_break.py`.

## Scenario 1 — Silent failure (metrics vs logs)

Hypothesis: `/debug/error` returns 500 and increments `http_requests_total` but emits no error log.

Disproved for that endpoint:
- `S1_DEBUG_ERROR_STATUS 500`
- `S1_ERROR_LOG_COUNT 1`
- `S1_SILENT_500 False`
- Log line includes `ERROR unhandled exception` and `request_id=req-d2a6ca95` plus `RuntimeError` stack trace.

Related gap that **is** silent (environment-proven, not the handler-swallow case):
- `/ready` (and other `engine.connect()` paths) hang when Postgres is down.
- A prior SQLAlchemy `engine.connect()` was killed after ~30s with no result.
- An ASGI `GET /ready` was killed after blocking the script; `asyncio.wait_for` did not recover because the wait sits behind a blocking DB connect.
- Effect: no HTTP 500, no error log, no completed `http_requests_total` sample for that request. Metrics stay green while the worker is stuck.
- This is a pillar gap: logs/metrics only observe **completed** requests. A hung dependency is invisible until scrape/`up` fails.

Not claimed: an error handler currently swallows `/debug/error` logs. It does not.

## Scenario 2 — Cardinality bomb

Hypothesis: `http_requests_total` labels use raw `request.url.path`, so unbounded path values explode time series.

Confirmed:
- Metric labels in `api/app/main.py` use `path=request.url.path`.
- 12 requests to `/ghost/0` … `/ghost/11` (404) produced 12 unique label values:
  `S2_GHOST_UNIQUE_COUNT 12`, `S2_CARDINALITY_BOMB_ON_RAW_PATH True`.
- Same pattern would apply to `/r/{code}` (one series per short code) and any unique 404.

## Scenario 3 — Missing request_id on inner logs

Hypothesis: middleware binds `request_id`, but business `emit_log` calls do not, so events cannot be joined.

Confirmed:
- `create_link` calls `emit_log("info", "link created", ...)` with no `request_id`.
- Reproducing that call: `S3_INNER_BUSINESS_LOG ... request_id=- ...`
- `S3_INNER_REQUEST_ID_MISSING True`
- Middleware request logs use `req-...`; inner logs use `-`. Correlation is broken.

## What FIX should change
1. Keep 5xx error logs (already present); treat hung DB as a documented limitation plus planned query timeout (not faked as a completed 500).
2. Label metrics with route templates (or `/unmatched`), never raw unique paths.
3. Bind `request_id` on a contextvar so every `emit_log` inherits it.
