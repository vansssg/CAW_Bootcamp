# Runbook: HighErrorRate

Alert fires when 5xx rate / total request rate exceeds 5% for 2 minutes.

1. Confirm `/metrics` is reachable and inspect `http_requests_total{status=~"5.."}`.
2. Correlate `request_id` from error logs (`level=error`, `message=unhandled exception` or `request failed`).
3. Check `/live` vs `/ready`: process up but DB down should keep `/live` 200 and fail `/ready`.
4. If errors concentrate on `/links` or `/r/{code}`, treat as dependency (Postgres) rather than process crash.
5. Mitigate: fail closed on writes, keep redirects/read paths if still healthy, then restore DB.
