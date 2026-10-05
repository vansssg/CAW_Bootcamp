# Postmortem: Missing contracts between cache, pool, auth, and CI

## Summary

Over Modules 05–06 the URL shortener failed at layer boundaries, not inside a single function. Module 05 recorded a SEV1 admin-auth bypass: empty/malformed `Authorization` values were treated as authenticated; lab impact was **12 short links across 8 accounts** (PITR clone target **2024-03-15 14:20:00 UTC**). On **2026-08-17** a vertical delete trace showed cache-first `GET /r` could serve a mapping after SoT removal; delete+recreate of `deadbeef` doubled analytics **2 → 4**; a failing click persist retried **6 times in 3.107s** with delays `[0.1, 0.2, 0.4, 0.8, 1.6]` then dead-lettered. `/live` stayed **200 in 0.003s**. Unknown: how long the auth bypass existed before the Module 05 lab window; live SQLAlchemy pool fill was **not** observed because `localhost:5432` still times out.

## Timeline (all times UTC)

### Auth bypass (Module 05 lab records)

- 2024-03-15 ~14:20 — PITR recovery target used in the restore plan (`progress/debugging-module5-fix.md`). Exact exploit-start second is **unknown**.
- Module 05 BUILD — SEV1 declared from repeated `200` on admin DELETE from an unrecognized source.
- Module 05 BUILD — `extract_bearer_token` / `require_admin_auth`: empty and whitespace headers → `401 Authorization required`.
- Module 05 BREAK/FIX — 12 deleted links / 8 accounts; restore plan written. **This workspace never ran a live Postgres restore** (5432 down).

### Cache / queue contracts (measured 2026-08-17)

- 08:03:46.217Z — `POST /links` 200 `persisted=memory`; `GET /r` 307; cache hit on in-process map (`REDIS_DOWN True`).
- 08:03:46.224Z — `DELETE /links/{code}` 200; `cache_invalidate`; SoT `code in links` **False**.
- 08:03:46.227Z — `GET /r` **404** in 0.002s (Bug #9 happy path with invalidate).
- 08:05:37.412Z — Seeded stale cache after `links.pop` without invalidate: `cache_sot_mismatch` then **404**.
- 08:05:37.414Z–08:05:40.520Z — `job_retry_backoff` attempts 1–5 (`delay_ms` 100, 200, 400, 800, 1600); `job_dead_letter attempts=6`; `/live` 200 in 0.003s.
- 08:07:33Z — Recreate same code `deadbeef`: `BEFORE_DELETE_CLICKS 2`, `AFTER_DELETE_EVENTS 2`, `AFTER_RECREATE_CLICKS 4`, `DOUBLED True`.
- 08:09:39Z — After namespaced keys + `purge_events_for_code`: `AFTER_DELETE_EVENTS 0`, `AFTER_RECREATE_CLICKS 2`, `DOUBLED False`; `link:redirect:deadbeef` vs `analytics:dedup:*` disjoint.

## Root Cause

Three defects, one class: **untested contracts**.

1. **Auth:** `require_admin_auth` previously accepted missing/empty `Authorization`. Fix is strict parse + 401 (Module 05). Exact pre-fix line is in that lab, not re-opened here.
2. **Redirect cache:** `GET /r` returned cache before SoT. DELETE already called `invalidate_redirect_target`; a cache hit with `code not in links` still 307 until `cache_sot_mismatch`. Redis key was later `redir:{code}` then `link:redirect:{code}`.
3. **Worker vs API:** click persist could retry with no backoff on the **same** SQLAlchemy pool as `/ready`. Fix: `worker_engine` `pool_size=2`, `JOB_RETRY_MAX=5`, exponential delays, DLQ. Default persist does not `SELECT 1` unless `JOB_PERSIST_DB=1` (down Postgres would stall ~4s per attempt).

The BREAK doubling was leftover `_events` for the same `short_code` plus a shared in-process key map, not a person “forgetting Redis.”

## Contributing Factors

1. **CI does not run contract tests.** `.github/workflows/ci.yml` runs ruff (`E9,F63,F7,F82`) and `test_query_columns.py` (string assert on a seed query). It does not run `module06_break_recreate.py`, `module04_auth_verify.py`, or `module06_multilayer_probe.py`.
2. **Health that cannot see the failure.** `/live` is `{ok:true}` with no DB. `/ready` is the pool/`SELECT 1` path. A worker storm that starved `engine` would look like a down API on `/ready` while `/live` stayed green — same class as an S3-hosted status page.
3. **One key space, two jobs.** Redirect cache used the short code as the map key; analytics dedup used `job_id` in a Python set. Invalidating the redirect entry did not define a second prefix, so recreate reused the code while `_events` still held old clicks.
4. **No merge gate for DELETE→GET /r.** Manual QA creates and reads short links. TTL (`TTL_S=60`) makes a stale redirect look “fixed” after a minute. Deletes are rare in that workflow.
5. **Shared pool by default.** One `create_engine` served `/ready` and any worker persist. Growing `pool_size` would only delay exhaustion; isolation was missing until `worker_engine`.
6. **Contract tests ran only against the in-process cache.** Redis was down (`REDIS_DOWN True`), so prefixes were proven in `_local`. A local “test passed” would still miss a shared Redis keyspace — same class as a migration that passes on tiny local data and fails on production-sized `users`.

## Impact

- **Duration:** Auth lab window ~10 minutes of documented exploitation (Module 05); vulnerability age before that **unknown**. Cache/analytics defects were latent until 2026-08-17 traces (seconds of probe time, not a user-facing outage on this laptop).
- **Users affected:** Module 05: owners of 12 links / 8 accounts (lab). Module 06: no production traffic here; probes used `principal-a` and code `deadbeef`.
- **Data affected:** 12 lab deletions (restore **not** executed — Postgres down). Analytics doubled 2→4 on recreate until purge. No durable Postgres writes (`persisted=memory`).

## Resolution

- Auth: `extract_bearer_token` + `require_admin_auth` → 401 on empty/whitespace/malformed (Module 05 verify matrix).
- Cache: invalidate on DELETE/PATCH; SoT check on cache hit; prefixes `link:redirect:` and `analytics:dedup:`.
- Queue: `process_job_with_retry`, DLQ, `worker_engine` bulkhead.
- Recreate: `purge_events_for_code` on DELETE. Re-test: `DOUBLED False`.

## Remediation Items

| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | Add a CI job with a Redis service container that runs `python app/scripts/module06_break_recreate.py` and fails if `DOUBLED` is true, namespaces are not disjoint, or `REDIS_DOWN` is true (do not accept an in-process-only pass) | Platform (GitHub Actions) | 2026-08-24 | Open |
| 2 | Create GitHub Actions secrets `API_KEY_A`, `API_KEY_B`, `JWT_SECRET` from local `api/.env` (never commit `.env`). Add a `test` job step: `python app/scripts/module04_auth_verify.py` with those env vars. Fail the job if any empty, whitespace, or malformed `Authorization` case is not HTTP 401 | Platform | 2026-08-24 | Open |
| 3 | Add a Prometheus (or log-based, if scrape is down) alert: `worker_engine` `checkedout == WORKER_POOL_SIZE` (2) for >10s OR `job_retry_backoff` count > 5/min OR `cache_sot_mismatch` count > 0. Route to the on-call channel. Do not page on `/live` 200 or on API 5xx alone | SRE | 2026-08-31 | Open |
| 4 | Keep `JOB_PERSIST_DB` default unset; if enabled, document 4s TCP timeout on this host and require `worker_engine` only | Backend | 2026-08-24 | Open (default already off) |
| 5 | CODEOWNERS: `api/app/auth.py`, `api/app/cache.py`, `api/app/jobs.py`, `api/app/db.py` require one `@platform` review before merge. Reviewer must confirm DELETE then GET /r 404, recreate not doubled, prefixes `link:redirect` vs `analytics:dedup`. A self-checkbox is not a merge gate | Engineering manager | 2026-08-24 | Open |

No item is “be more careful.” None names a person.

## Lessons Learned

- **Went well:** Vertical delete trace disproved “DELETE lied” before anyone proposed lowering TTL. BREAK captured `DOUBLED True` before the namespace fix. `/live` 200 during retries was recorded instead of assumed.
- **Went poorly:** CI still would not catch recreate doubling. Auth restore was written, not run (5432). Redis down so “two Redis prefixes” were proven only in `_local`.
- **Lucky:** Redis timeout forced the in-process map, so we could inspect keys without a live cluster. Postgres never accepted connections, so a real pool-exhaustion outage did not happen during the retry drill. Next time those two luck items are gone: a live Redis with a shared prefix, or `JOB_PERSIST_DB=1` against a hanging 5432, would not be free.

## Highest-impact lesson (VERIFY)

If the team absorbs one thing: **layer-boundary contracts must fail the merge.** Lint plus `test_query_columns.py` would still ship the auth empty-header bypass, the cache-after-DELETE 307, and recreate doubling. A new engineer handed remediation #1 can add the recreate job without asking what “improve testing” means. That one CI gate prevents the largest class of the ten bugs repeating.
