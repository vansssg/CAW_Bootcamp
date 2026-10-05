# Module 07 BREAK — follow postgres-unreachable.md after an unannounced change

Pager: `/live` 200, writes failing. Followed `docs/runbooks/postgres-unreachable.md` as written. Did not skip steps.

## Runbook Step 1 `/live`

Command as written.

- Expected: `200 {"ok":true}` ~0.05s
- Actual: `STEP1_LIVE 200 {"ok":true}` (log `path=/live status=200 duration_ms=2`)

Matches the “process is alive” row. Continue.

## Runbook Step 2 `/ready` once

Command as written.

- Expected IS-problem: `status 503 secs 4.0–4.5` body `error.code=service_unavailable`
- Expected NOT-problem: status `200` under 1s
- **Actual: `STEP2_READY status 404 secs 0.008 b'{"detail":"Not Found"}'`**
  - log: `path=/ready status=404 duration_ms=0`

That result is on **neither** branch. The runbook has no next step. Stop. Do not invent a docker start. Do not loop `/ready`.

## What the runbook cannot explain

A 404 in 8ms is not a Postgres timeout (those were 4.082s 503 on this host) and not a healthy ready (200). The diagnosis table is stale relative to the process that just answered `/live`.

## Honest bound

Did not `docker stop` / `docker start`. Docker daemon still missing `dockerDesktopLinuxEngine`. The break is the runbook vs the live route table, not a recovered database.
