# Production Readiness Module 04 REFLECT

## Decision callback (choice B: hybrid logs + pull Prometheus)

Kept hybrid. Pretty development lines made `request_id=-` on `link created` obvious (`S3_INNER_BUSINESS_LOG`). JSON-always would have hidden that as a field that looks "present" (`"-"` or null) inside a blob. Would not switch to JSON-always for local work; production still needs JSON for aggregation.

Kept pull `/metrics`. Cardinality showed up as 12 distinct `path=/ghost/N` series, then after FIX a single `path=/unmatched` series. That is a scrape-side symptom. Serverless would change this: no long-lived scrape target, so push/OTLP would fit better; we did not implement push.

## Hard question
Worse: too many alerts. HighErrorRate stays at 5% for 2m (not 1%) specifically so a single `/debug/error` in a quiet process does not page. You can add alerts; you cannot un-train pager ignore.

## If only one pillar
Metrics first. `/metrics` told us 12 unique ghost paths and `status="500"` on `/debug/error` before we grepped logs. Logs then explained WHY (`RuntimeError` + `req-fix-500`). Without metrics we would not know WHEN to look.

## Knowledge check
1. Core problem: the service was flying blind — completed requests had no joinable logs, low-cardinality metrics, or pageable alerts.
2. Biggest-impact decision: hybrid + pull. Hybrid caught missing `request_id` by eye; pull made the cardinality bomb a `/metrics` series explosion we could count.
3. End-to-end evidence: BUILD drill (`/live` 9 x 200, `/debug/error` 500 + stack), BREAK (`S2_GHOST_UNIQUE_COUNT 12`, `request_id=-`), FIX (`FIX_UNMATCHED_SERIES 12`, `request_id=req-fix-inner`, `status=500` metric).

## Mini practical (VERIFY-style)
Command: `api/.venv/Scripts/python.exe app/scripts/module04_observability_fix.py`
- `FIX_DEBUG_ERROR_STATUS 500`
- `FIX_DEBUG_500_METRIC [('/debug/error', '500', 1.0)]`
- `FIX_ERROR_LOG_HAS_STACK True` (`RuntimeError: forced observability test error`)
- `FIX_INNER_LOG_INHERITS_REQUEST_ID True`

## Risk + mitigation
Risk: raw `request.url.path` as a Prometheus label (`/r/{code}`, random 404s) unbounded time series, slow scrapes, memory growth.
Mitigation implemented: `metric_path()` uses route templates or `/unmatched`. Per-code detail stays in logs via `request_id` and path field, not metric labels.

## Limitation (not implemented)
Postgres `engine.connect()` hang on `/ready` still has no timeout. That is a planned Module 05/06 failure-mode/degradation item, not a completed 500.
