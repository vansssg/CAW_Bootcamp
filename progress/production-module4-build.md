# Production Readiness Module 04 BUILD Evidence

## Decision applied
- Log format: **hybrid** (`APP_ENV=development` pretty lines, otherwise JSON).
- Metrics: **pull-based Prometheus** via `GET /metrics`.

## Implemented (code)
- `api/app/main.py`
  - `emit_log()` always includes `timestamp`, `level`, `message`, `service_name`, `request_id`.
  - Request middleware honors `X-Request-ID` or generates `req-<8 hex>`, echoes it on the response.
  - Counter `http_requests_total{method,path,status}`, histogram `http_request_duration_seconds{method,path}`, gauge `urls_total`.
  - `GET /metrics` returns `prometheus_client.generate_latest()`.
  - `GET /debug/error` raises `RuntimeError` so error logs include a stack trace.
  - Unhandled exceptions return HTTP 500 and increment `status="500"`.
- `api/requirements.txt`: `prometheus-client`.
- Alert rules: `progress/production-module4-alert-rules.yml` (`HighErrorRate` 5%/2m critical, `HighLatencyP95` >2s/3m warning, `ServiceDown` `up==0`/1m critical).
- Runbooks: `progress/production-module4-runbook-*.md`.

## Failure-first drill (real command)
Command:
`api/.venv/Scripts/python.exe app/scripts/module04_observability_verify.py`

ASGI HTTP-scope only (no FastAPI lifespan), so `/live` and `/metrics` run without Postgres startup.

Observed:
- `DEV_HAS_*` all True for pretty logs (timestamp, INFO, message, `service_name=url-shortener`, `request_id`).
- Production JSON required keys True: `timestamp`, `level`, `message`, `service_name`, `request_id`.
- Mixed requests: 8x `/live` + `/health` + honored `/live` = `LIVE_STATUSES` ten `200`s.
- `HONORED_X_REQUEST_ID req-upstream-abc`.
- `DEBUG_ERROR_STATUS 500` with log `ERROR unhandled exception` and `RuntimeError: forced observability test error`.
- `http_requests_total{method="GET",path="/live",status="200"} 9.0`
- `http_requests_total{method="GET",path="/debug/error",status="500"} 1.0`
- Histogram buckets present for `/live`.
- Gauge `urls_total` present.

## Environment blocker (not fabricated)
- Postgres `localhost:5432` and Redis `localhost:6379` are not serving connections in this environment.
- SQLAlchemy `engine.connect()` hung with no `SELECT 1` result and was killed after ~30s.
- Therefore live `uvicorn` startup (`verify_database_connection`) cannot be used for this drill.
- Distinguishing implemented vs not run: observability code is implemented and proven over ASGI; live scrape of a long-running uvicorn process was not run because startup blocks on DB.
