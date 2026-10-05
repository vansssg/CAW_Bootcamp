# Module 01 Diagnosis Notes

## Bug 1
- Symptom: API startup fails before serving traffic.
- Hypothesis A:
  - Command: `docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"`
  - Observation: Postgres service was running (`upsk-sdf-postgres` on `5432`), so "DB process is down" was disproven.
- Hypothesis B:
  - Command: `./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 3000`
  - Observation: Startup crashed with `ValueError: DATABASE_URL environment variable is required.` while `.env` had `DB_URL`, confirming a config contract mismatch.
- Fix: (intentionally deferred for module workflow)
- Fix: Renamed `DB_URL` to `DATABASE_URL` in `.env` to match the app config contract, then aligned DB target to the active local Postgres database (`upsk_sdf`) on `5432`.
- Verification proof: `./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 3020` reached `Application startup complete`, and `curl -sS http://127.0.0.1:3020/health` returned `{"ok":true}`.

## Bug 2
- Symptom: Paginated `/api/admin/links` results overlap between page boundaries.
- Hypothesis A:
  - Command: `./.venv/Scripts/python.exe -c "<fetch page=1 and page=2, compare short_code overlap>"`
  - Observation: Page 1 ended with `test09`; page 2 started with `test09`; overlap detected (`['test09']`) which supports offset math bug.
- Hypothesis B:
  - Command: Review list query behavior (`LIMIT/OFFSET` without `ORDER BY`) through endpoint output and SQL path.
  - Observation: No explicit ordering contract exists, so result ordering can drift and worsen boundary duplication under concurrent writes.
- Fix: Corrected offset formula to `offset = (page - 1) * limit` and added deterministic query ordering with `ORDER BY id ASC`.
- Verification proof: Page checks on `limit=10` returned `page1: abc123..test09`, `page2: test10..test19`, `page3: test20..test25`; overlaps were empty, repeated requests for each page were identical, and combined unique records (`26`) matched `SELECT COUNT(*) FROM links` (`26`).

## Module 03 - Race Condition in Redirect Analytics

### Hypothesis
- The intermittent `500` on redirect is caused by a concurrency race in analytics writes: a check-then-insert flow allows two concurrent requests to see "no row" and both attempt `INSERT` for the same `(link_id, timestamp_bucket)`, triggering `analytics_link_id_bucket_unique`.

### Test
- Reproduction conditions: `30` concurrent requests, `5` rounds, same short code target.
- Command: `REPRO_BASE_URL="http://127.0.0.1:3044" REPRO_CONCURRENCY=30 REPRO_ROUNDS=5 ./.venv/Scripts/python.exe app/scripts/module-03-repro-race.py`
- Pre-fix implementation under test: redirect analytics path intentionally used vulnerable check-then-insert logic.
- Post-fix command (identical load profile): `REPRO_BASE_URL="http://127.0.0.1:3045" REPRO_CONCURRENCY=30 REPRO_ROUNDS=5 ./.venv/Scripts/python.exe app/scripts/module-03-repro-race.py`

### Observation
- Pre-fix evidence:
  - Round 1 returned mixed statuses: `{"307": 29, "500": 1}`.
  - Script result: `BUG REPRODUCED: observed HTTP 500 under concurrent load.`
  - Server logs showed: `duplicate key value violates unique constraint "analytics_link_id_bucket_unique"` (`UniqueViolation`).
- Fix applied:
  - Replaced check-then-insert with atomic Postgres upsert:
    - `INSERT ... ON CONFLICT (link_id, timestamp_bucket) DO UPDATE SET count = analytics.count + 1, last_accessed_at = NOW()`
- Post-fix evidence:
  - All rounds returned only `307` responses (`{"307": 30}` each round).
  - Script result: `NO REPRO: no HTTP 500 observed under current test conditions.`
  - Log scan after fix found no `UniqueViolation` entries.

### Conclusion
- The race condition root cause was confirmed as non-atomic check-then-insert in redirect analytics writes.
- Converting the write to a single atomic `ON CONFLICT DO UPDATE` operation eliminated the duplicate-key failure under the same concurrency workload.
