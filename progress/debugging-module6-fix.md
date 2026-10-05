# Debugging Module 06 FIX — separate key namespaces

Bug #9 invalidation was correct (`DEL` redirect only). BREAK doubling was leftover `_events` plus a shared key space (`_local[code]` vs job ids). Redirect and analytics now use distinct prefixes.

- Redirect: `link:redirect:<short_code>`
- Dedup: `analytics:dedup:<job_id>`
- `invalidate_redirect_target` deletes only the redirect key
- DELETE also `purge_events_for_code` so a reused code does not inherit old clicks

Redis still down: namespaces verified in the in-process map.

## Re-test (`module06_break_recreate.py`)

- BEFORE_DELETE_CLICKS 2
- AFTER_DELETE_EVENTS 0
- AFTER_RECREATE_CLICKS 2
- DOUBLED False
- REDIRECT_KEYS `['link:redirect:deadbeef']`
- DEDUP_KEYS_PREFIX_OK True
- NAMESPACES_DISJOINT True

module07_jobs_verify JOBS:0; module06_cache_verify CACHE:0 (PATCH still avoids stale URL).
