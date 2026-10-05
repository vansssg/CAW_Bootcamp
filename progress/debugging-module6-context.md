# Debugging Module 06 CONTEXT — boundaries, not components

Health checks that ask each part “do you work?” miss contracts. Connection pool exhaustion: parking lot full, gates still open. Cascading failure: queue retries starve the API’s pool.

## Three boundaries (this shortener)

### 1. Redirect path ↔ cache ↔ mapping store

Hand-off: `GET /r/{code}` calls `get_redirect_target` then the in-process `links` dict (`api/app/cache.py`, `api/app/main.py`).

Receiver assumption: cache entry is current with the mapping. Enforced only by `invalidate_redirect_target` on PATCH and a 60s TTL. **Not** enforced on in-memory FIFO eviction (`MAX_IN_MEMORY_LINKS=10000`) or a Postgres delete that never happened because creates are `persisted=memory`. Cache can 307 to a code the dict already dropped.

### 2. HTTP workers ↔ SQLAlchemy pool ↔ Postgres

Hand-off: `/ready` `SELECT 1` and startup `verify_database_connection` borrow from `engine` (`pool_timeout=1`, `connect_timeout=1`).

Receiver assumption: a checkout means the database can serve the next business query. **False here:** `/ready` 503 ~4s `postgres_connect_or_query_timeout` while `POST /links` 200 `persisted=memory`. Pool/health is not the write path. Five `/ready` probes open pybreaker; looping ready is how you fill the lot.

### 3. Redirect/click enqueue ↔ in-process `queue.Queue` ↔ analytics `_events`

Hand-off: `enqueue_click` → `drain_once` → `_events` (`api/app/jobs.py`).

Receiver assumption: a “queued” click will be readable on `GET /links/{code}/analytics`. Enforced by calling `drain_once()` in the analytics handler, not by a worker process. If drain does not run, the queue looks healthy (`Queue()` accepts puts) and analytics is empty. Caps `MAX_EVENTS=10000` drop old events without telling the API. Same process as the pool — a retry storm would be a cascade into checkouts, not a separate host.

## What is only believed

No doc says “cache TTL vs dict eviction” or “SELECT 1 ≠ INSERT.” Module 07 `/ready` 200 vs user 404 runbook is the first place that contract is written down.
