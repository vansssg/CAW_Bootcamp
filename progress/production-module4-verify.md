# Production Readiness Module 04 VERIFY Evidence

## Metrics
Command: `api/.venv/Scripts/python.exe app/scripts/module04_observability_verify.py` (ASGI, no lifespan).

- `METRICS_STATUS 200`
- Counter by method/path/status: `http_requests_total{method="GET",path="/live",status="200"} 9.0`
- 500 series: `http_requests_total{method="GET",path="/debug/error",status="500"} 1.0`
- Histogram buckets populated, e.g. `http_request_duration_seconds_bucket{le="0.005",method="GET",path="/live"} 8.0`
- Gauge present: `urls_total` in `/metrics` output (`METRICS_HAS_GAUGE True`)

Not claimed: live Prometheus scrape of a uvicorn process. Startup still blocks on Postgres (`engine.connect()` hung; process killed).

## Structured logging
Hybrid decision is in force (`APP_ENV=development` in `.env`).

Development request line (real ASGI `/live` with `X-Request-ID: req-upstream-abc`):
- pretty format includes timestamp, `INFO`, `request completed`, `service_name=url-shortener`, `request_id=req-upstream-abc`
- response header `HONORED_X_REQUEST_ID req-upstream-abc`

JSON contract (formatter path already executed in the same verify script by rendering `emit_log` as JSON):
- `PROD_JSON_REQUIRED_OK True`
- keys: `level`, `message`, `request_id`, `service_name`, `stack_trace`, `status`, `timestamp`
- `PROD_JSON_LEVEL error`, `PROD_JSON_REQUEST_ID req-verify02`

Did not switch the running service `APP_ENV` to production for HTTP; JSON proof is the formatter output, not a production process.

## Error logging
- `DEBUG_ERROR_STATUS 500` for `GET /debug/error`
- Same request id on response: `DEBUG_ERROR_REQUEST_ID req-fc01b1af`
- Log: `ERROR unhandled exception ... request_id=req-fc01b1af ... stack_trace=... RuntimeError: forced observability test error`
- Metric: `status="500"` increment on `/debug/error`

## Alerts complete
File: `progress/production-module4-alert-rules.yml`
- 3 alerts, each with `expr`, `for`, `severity`, `summary`, `description`, `runbook` (counts: 3 each)
- HighErrorRate: 5% / 2m / critical / runbook `production-module4-runbook-high-error-rate.md`
- HighLatencyP95: p95 > 2s / 3m / warning / runbook `production-module4-runbook-high-latency.md`
- ServiceDown: `up == 0` / 1m / critical / runbook `production-module4-runbook-service-down.md`

## Conceptual answers (VERIFY)
3 AM after HighErrorRate: first `/metrics` (or Grafana) to see **which paths/status codes** moved, then logs filtered by `level=error` and those paths' `request_id`s for stack traces. Alert says THAT; metrics say WHAT; logs say WHY.

Observability vs monitoring: monitoring is the predefined HighErrorRate 5%/2m watch. Observability is being able to ask a new question from the same signals — e.g. only `/debug/error` produced `status="500"` while `/live` stayed 200, correlated by `request_id`.

## Red flags checked
- Logs do not emit `JWT_SECRET`, `DATABASE_URL`, or request bodies. URLs are sanitized for CR/LF only; they are business data for a shortener, not credentials.
- Alert messages name the condition, threshold, and runbook path — not "something is wrong".
