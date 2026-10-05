# Runbook: HighLatencyP95

Alert fires when histogram p95 of `http_request_duration_seconds` exceeds 2s for 3 minutes.

1. Inspect histogram buckets on `/metrics` by path.
2. Separate `/live` (in-process) from DB-backed `/ready`, `/links`, `/r/{code}`.
3. If only DB paths are slow, check Postgres connectivity and query time; do not restart a healthy process first.
4. If `/live` itself is slow, inspect CPU and request-size handling (`MAX_URL_LENGTH`).
5. Escalate to critical only if p95 > 5s or the condition lasts > 10 minutes.
