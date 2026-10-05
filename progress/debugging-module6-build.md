# Debugging Module 06 BUILD — Bugs 9 and 10

Vertical traces. Redis down (`TimeoutError`); SoT is the in-process `links` dict, not Postgres. Pool checkouts to 5432 still time out (~4s); live pool exhaustion was not observed because connects never succeed.

## Bug #9 — stale cache after DELETE

H1: DELETE returned 200 but SoT still had the code.  
Test: after `DELETE /links/{code}`, `code in links` is **False**. H1 disproved.

H2: SoT gone, cache still serving. Redirect reads cache first (`get_redirect_target`).  
Warm `GET /r` → 307, `cache_hit`. Owner DELETE already called `invalidate_redirect_target` → `GET /r` **404 in 0.002s**. Redis was not holding a key (daemon/cache down).

Remaining contract hole: cache hit never asked SoT. Seeded stale cache after `links.pop` without invalidate:

- `SEEDED_STALE_CACHE True sot False`
- After SoT guard: `STALE_CACHE_REDIRECT 404`, log `cache_sot_mismatch reason=source_of_truth_missing`, cache then miss.

Fix: on cache hit, if `code not in links`, invalidate and 404. Delete still invalidates; this covers forgotten invalidation.

## Bug #10 — retry storm / shared pool

H1: API deadlock/CPU loop. `/live` stayed 200 in 0.002–0.003s. Not a dead process.

H2: shared pool exhausted by worker retries. `engine.pool is worker_engine.pool` was the design risk. Now **POOL_ISOLATED True** (`API_POOL_SIZE=5`, `WORKER_POOL_SIZE=2`, `max_overflow=0`).

Worker had no backoff, no max retries, no DLQ. Naive 6 immediate fails: `elapsed_s 0.0`. `process_job_with_retry` on `forced_job_fail`:

- `RETRY_RESULT dead_letter attempts 6 elapsed_s 3.107`
- `delays_s [0.1, 0.2, 0.4, 0.8, 1.6]`
- `LIVE_AFTER_STORM 200 elapsed_s 0.003`

Did not hold live TCP connections (Postgres down). Isolation is two engines; storm is the failing persist stub, not a filled QueuePool.

Default `persist_click` does not `SELECT 1` unless `JOB_PERSIST_DB=1`, so a down DB cannot stall every click 4s.
