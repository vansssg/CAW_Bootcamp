# Debugging Module 06 BREAK — duplicate analytics after delete+recreate

Hypothesis before code: cache.del on DELETE does not talk to the worker. Duplicate clicks on the same short_code after recreate means `_events` still holds rows for that code. Invalidation made DELETE “really gone” for `GET /r`, so the same code can be reused; analytics still summed the old jobs. Not a shared Redis key: worker idempotency is `_seen_job_ids` / `job_id`, cache is `redir:{code}` / `_local[code]`.

Measured 2026-08-17 (`module06_break_recreate.py`):
- BEFORE_DELETE_CLICKS 2
- DELETE_STATUS 200
- AFTER_DELETE_EVENTS 2  (not cleared)
- AFTER_RECREATE_CLICKS 4
- DOUBLED True

