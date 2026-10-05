# Debugging Module 06 VERIFY

## Bug #10 chain (this service)

1. Persist fails (`RuntimeError forced_job_fail` in the probe; on a live DB it would be the same OperationalError the click writer hit).
2. Worker retries **immediately** if there is no backoff (`NAIVE_IMMEDIATE_ATTEMPTS 6 elapsed_s 0.0`).
3. Each persist uses a DB checkout. Without a bulkhead that is `engine` (API pool), not `worker_engine`.
4. Retry fails again (same error).
5. No max → loop never stops.
6. Shared pool fills (`pool_size=5`, `max_overflow=0` on the API engine after the split).
7. API paths that checkout (`GET /ready` SELECT 1) wait on `pool_timeout=1`.
8. Those requests hang ~timeout, not crash. `/live` does **not** checkout — it stayed 200 in 0.003s.
9. If health is `/ready` not `/live`, probes time out.
10. Monitoring calls the API down.

**Steps:** 10 from persist fail to “API down” if readiness uses the pool. **Longest layer gap:** queue worker → SQLAlchemy pool → API request thread (three layers; symptom is HTTP, cause is job persist).

Measured after the fix: `dead_letter attempts 6 elapsed_s 3.107 delays_s [0.1, 0.2, 0.4, 0.8, 1.6]`. `/live` still 200. Live QueuePool fill was **not** seen: 5432 never accepts, so checkouts do not stay held.

## Bug #9 — why development missed it

Creates and `GET /r` are the happy path. Deletes are rare in manual QA. Cache TTL here is **60s** (`TTL_S`), not 5 minutes — after TTL the miss looks “fixed.” Redis was down so the layer was the in-process map; same contract. Lowering TTL is not the fix: seeded stale cache still 307 until SoT check / invalidate. We got **404** from invalidate on DELETE and from `cache_sot_mismatch` when SoT was popped without invalidate.

## One alert for Bug #10

Earliest signal: **worker pool checked-out == WORKER_POOL_SIZE (2) for > 10s**, or `job_retry_backoff` rate. Not API error rate (that is step 8–10). Not “increase pool size.”
