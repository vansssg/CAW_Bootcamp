# Debugging Module 07 VERIFY

Stress-tested `progress/debugging-module7-postmortem.md` against the lesson red flags.

## Contributing factors — subject is a system, not a person

Read each subject out loud:

1. **CI** does not run contract tests — toolchain.
2. **Health that cannot see the failure** (`/live` vs `/ready`) — endpoints.
3. **One key space, two jobs** — cache/map design.
4. **No merge gate for DELETE→GET /r** — pipeline, not “QA forgot.”
5. **Shared pool by default** — `create_engine` wiring.

None start with “The developer” or “Someone.” No “should have known.” Grep of the postmortem for those blame stems hits only the explicit “No item is be more careful” line.

## Remediations — new engineer, zero clarifying questions

| # | Pass? | Why |
|---|-------|-----|
| 1 | Yes | Exact script `module06_break_recreate.py`; fail if `DOUBLED` true or namespaces not disjoint. |
| 2 | Tightened | Named secrets `API_KEY_A`/`API_KEY_B`/`JWT_SECRET`, exact script, fail if empty/whitespace/malformed Authorization is not 401. |
| 3 | Tightened | Threshold `checkedout == 2` for >10s or `job_retry_backoff` >5/min; not `/live`. |
| 4 | Yes | Keep `JOB_PERSIST_DB` unset; if on, document 4s TCP timeout and `worker_engine` only. |
| 5 | Yes | PR checkbox with the three contracts, not “be careful about auth.” |

Vague “improve testing” is not in the table.

## Timeline

Not “around midday.” Auth PITR target **2024-03-15 14:20 UTC**. Cache/queue probes **2026-08-17 08:03:46.217Z–08:09:39Z** with millisecond lines from the multilayer script.

## Incident report vs learning document

Resolution plus five Open remediations with owners and deadlines. It is not “what happened” only.

## One lesson that prevents the most future incidents

**CI must fail on layer-boundary contracts.** Not the most interesting (pool bulkhead). The largest impact: if recreate doubling, empty Authorization, and DELETE→GET /r 404 are merge gates, the class of untested contracts that produced Bugs 8–10 cannot ship again by lint-only CI.

Evidence CI still misses them: `.github/workflows/ci.yml` jobs are ruff `E9,F63,F7,F82` and `test_query_columns.py`. Grep of `.github` for `module06_break_recreate` / `module04_auth_verify` / `module06_multilayer` is empty.
