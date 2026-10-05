# S3 2017 interlude — applied to this shortener

US-East-1 index taken down by a playbook parameter; status page assets lived on S3 so the dashboard stayed green; logs and health checks shared the failing dependency.

## Circular monitoring here

`/metrics`, structured logs, and `/live` all run in `api/app/main.py`. `/live` does not checkout Postgres, so it stays 200 while `/ready` is 503 ~4s (`postgres_connect_or_query_timeout`). Trusting `/live` (or an in-process scrape) is the S3 status page. There is no independent scraper on this laptop. `HighErrorRate` never fires if 5xx never leave the process.

Click analytics `_events` and the worker live in the same process as the API. If that process hangs on pool checkout, you lose both the symptom and the job log.

## Missing guardrails

- `docker rm` vs `docker restart` (Module 07 runbooks): a wrong container name is an S3-style parameter with no upper bound.
- `JOB_PERSIST_DB=1` would make every click `SELECT 1` on a down 5432 (~4s). Default is off.
- Compose `DATABASE_URL` override is a UI/file edit not a SHA. `/ready` `image_sha` is `unknown` unless `IMAGE_TAG` is set.

## System change, not “be careful”

Remediation already in code: `worker_engine` bulkhead, `JOB_RETRY_MAX=5` + backoff, `link:redirect:` vs `analytics:dedup:`, `/ready` checks not `/live` for traffic. Module 07 postmortem must not say “remember to invalidate cache.”
