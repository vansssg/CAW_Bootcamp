# Debugging Module 07 REFLECT

## Scope decision (B broad)

Chose **B** in DECIDE: one postmortem on the untested-contract class across auth, cache/SoT, worker pool, and key prefixes — not Bug #8 only.

What it cost: pressure toward “insufficient testing.” What we did instead: cap **five** remediations, each a command or CODEOWNERS path. FIX still had to replace the PR checkbox (human) with required review (merge gate), which is the broad-scope failure mode the lesson warned about.

Audience (pipeline owners) was served better by B: CI still only runs ruff + `test_query_columns.py`. A Bug-8-only doc would have stopped at `require_admin_auth`. Next one-bug SEV1 with a clean timeline: choose A.

## Inversion test (contributing factors)

| Factor | This bug only? | Class? |
|--------|----------------|--------|
| CI missing recreate/auth scripts | Recreate doubling / empty Authorization | **Class:** untested layer contracts |
| `/live` vs `/ready` | Worker storm looks like API down | **Class:** health that cannot see the failure |
| One key space | Recreate analytics | **Class:** shared map, two jobs |
| No DELETE→GET /r merge gate | Bug #9 | This path, plus any cache-first read |
| Shared `create_engine` | Bug #10 | **Class:** no bulkhead |
| In-process-only cache proof | This laptop (`REDIS_DOWN`) | **Class:** local pass ≠ production-like dependency |

Highest leverage remains **contracts fail the merge**, not a bigger pool or lower TTL.

## New-engineer test (remediations)

1. Redis service + `module06_break_recreate.py`; fail if `DOUBLED` or `REDIS_DOWN`.
2. Actions secrets + `module04_auth_verify.py` 401 matrix.
3. Alert: worker `checkedout==2` >10s, `job_retry_backoff` >5/min, `cache_sot_mismatch` >0.
4. `JOB_PERSIST_DB` default unset.
5. CODEOWNERS on `auth.py`/`cache.py`/`jobs.py`/`db.py`.

None are “be careful.” Status is **Open** — not executed in `.github/workflows/ci.yml` (grep empty).

## Blameless culture (one sentence)

Blameless means the write-up names the missing gate that let a bad header, a stale cache hit, or a shared pool reach users — not the person who typed the line.

## Knowledge check

1. **Core problem:** postmortems that blame people and prescribe caution do not change the system, so the next engineer hits the same hole.
2. **Biggest decision:** broad vs narrow scope. Broad made the CI gap visible; the risk was vague remediations; CODEOWNERS and exact scripts were the correction.
3. **End-to-end proof:** `progress/debugging-module7-postmortem.md` has UTC timestamps (`08:03:46.217Z`, PITR `2024-03-15 14:20`), 12 links / 8 accounts, clicks 2→4 then 2, five owned remediations; BREAK listed 16 failures in the John doc; FIX rewrote root cause as the migration pipeline.

### Mini VERIFY (STEP 4 action)

Grep of our postmortem for `The developer|Someone|John |be more careful|should have known` → only the explicit “No item is be more careful” line.

Grep of `.github/workflows/ci.yml` for `module06_break_recreate|module04_auth_verify|CODEOWNERS` → **no matches**. That is the remaining risk.

**Risk:** remediations still Open, so lint-only CI can still merge the eleventh bug.  
**Mitigation:** remediation 1 must fail if `REDIS_DOWN`; remediation 5 is a merge block, not a checkbox.

`progress/state.json`: module 07 complete, skill complete. UPSK skill completion still depends on accepted `upsk report` then `upsk next`.
