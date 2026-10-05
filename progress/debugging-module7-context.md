# Debugging Module 07 CONTEXT — blameless postmortem

Fixing ten bugs ended the incidents. It did not end the class: missing contracts between cache/SoT, worker/API pool, and key namespaces. A postmortem asks what the *system* allowed, then what we change so the class cannot recur.

## Blameless rewrite

Blame: "The junior developer pushed untested code to production, causing the outage."

Rewrite: "A change reached the serving process without a merge gate that required the delete-then-GET /r and delete-then-recreate analytics checks. CI (`.github/workflows/ci.yml`) runs ruff plus `test_query_columns.py` only; it does not run `module06_break_recreate.py`. The pipeline, not a person, is what allowed a cache/SoT contract miss to ship."

Subject is the pipeline. Not "the developer should have tested."

## Local facts this postmortem will use

- DELETE then GET /r 404 after invalidate; seeded stale cache 404 via `cache_sot_mismatch`.
- Recreate same code: clicks 2→4 until `purge_events_for_code` + `link:redirect:` vs `analytics:dedup:`.
- Worker retries: naive 6 in 0.0s vs DLQ after `[0.1, 0.2, 0.4, 0.8, 1.6]`. `/live` 200 in 0.003s.
- Postgres `localhost:5432` still times out; live pool fill was not observed.
