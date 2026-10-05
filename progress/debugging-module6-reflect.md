# Debugging Module 06 REFLECT

## Vertical after the fact

Chose **B vertical**. Delete → SoT (`links`) → cache is how Bug #9 showed up: H1 false (code gone), H2 the class (cache-first). Seeded stale cache without invalidate still 307 until `cache_sot_mismatch`. Would keep vertical for handoff bugs.

Bug #10 is not one request: `/live` 200 while a worker retry storm would starve `engine`. The useful question was “who else uses this pool?” Vertical on an API hang would have blamed FastAPI. Next time: vertical for a named action; for “API hung, no errors,” list shared resources first.

## Shared resource in this service

SQLAlchemy `engine` was shared by `/ready` and any worker persist. Also `_local` used bare `code` for redirects while jobs used `job_id` in a different structure — BREAK still doubled `_events` 2→4. After FIX: `link:redirect:` vs `analytics:dedup:`, `worker_engine` pool_size=2.

## Knowledge check

1. Core problem: each layer can be correct while the contract between them is missing (invalidate, bulkhead, key prefix).
2. Biggest decision: vertical vs horizontal. Vertical found delete/cache; Bug #10 needed “who holds the pool.”
3. Proof: DELETE then GET /r 404; seeded stale 404; recreate clicks 2 not 4; retry delays 0.1..1.6 then DLQ; /live 200 0.003s.

Mini VERIFY: `python app/scripts/module06_break_recreate.py` → DOUBLED False, NAMESPACES_DISJOINT True.

Risk: `JOB_PERSIST_DB=1` with down Postgres is ~4s per attempt. Mitigation: default persist no-op; worker pool isolated.

Would not lower TTL or grow the API pool.
