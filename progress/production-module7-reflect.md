# Production Module 07 REFLECT

## Format after testing

Chose **A linear checklist**. Still would. Walking postgres-unreachable as a stranger, every useful minute was “run this, match this output.” The BREAK cost of A showed up exactly as warned: Step 2 returned `404 0.008 {"detail":"Not Found"}`, which matched neither the 503~4s row nor the 200 row, and the list went silent.

Did not stay pure. Added Step 2b (path drift) so “output matches neither row” has a next command. Spine is still numbered; one failure branch is not a nested tree. Tradeoff accepted: extra Step 2b vs 3 AM staring at a 404 with no row.

## Used vs ignored

A used runbook has commands that were executed on this host and outputs that were pasted from that run. After the first walk we had to fix JSON spacing (`{"ok":true}` vs `{"ok": true}`), drop “4ms after one `/ready`” (READY2 was still 4.073s), and paste the Docker pipe error. An ignored runbook is a wiki that says “check Postgres” without those strings. Trust came from the drill tally (5 mismatches), not from the file existing.

## Onboard with today’s docs only

1. Read `docs/service-overview.md`: what it is, Postgres/Redis/Docker fallbacks, `/live` vs `/readyz`, env vs hardcoded `fail_max=5`, deploy `git push origin main`, rollback `git revert`, `#linkops-alerts` at 15 min.
2. On pager, pick one linear file under `docs/runbooks/` from the alert name.
3. Copy-paste. If `/readyz` is 503 ~4s, stay on postgres-unreachable. If `/ready` 404s, Step 2b.

Gaps: no ServiceDown runbook (process dead / import hang). `/readyz` 200 after a real Postgres start was never seen here. Docker Desktop down means the “compose up” step is escalate-only on this laptop.

## Prevent stale runbooks in production

Mechanics, not “keep it updated”:
- After every incident that used the file, patch expected output from the actual command (this module: 5 patches, then `/ready` → `/readyz`).
- In the PR that changes a health route or container name, the same PR edits `docs/runbooks/` and `docs/service-overview.md`.
- Scheduled re-walk of one runbook per week; owner is whoever last merged a health/infra change, else primary on-call.
- Smoke: the ASGI one-liners in the runbook, not a paragraph.

## Knowledge check

1. Core problem: 3 AM operators need executable procedures with expected output, not a wiki about the service.
2. Biggest decision: checklist vs tree. Checklist is followable under sleep debt; BREAK proved the cost — one stale path and the list has no branch until you add one.
3. End-to-end evidence: first drill LIVE 200 0.052 / READY 503 4.082; BREAK `/ready` 404 0.008; FIX `/readyz` 503 4.049; docker pipe missing; TCP TimeoutError.

## Mini VERIFY action (reproducible)

```
.venv/Scripts/python.exe -c "... asgi_request('/readyz') ..."
```
Result this session: `status 503 secs 4.049` `error.code=service_unavailable` `failure_mode=postgres_connect_or_query_timeout`.

## Risk / mitigation

Risk: a deploy renames `/readyz` again and on-call treats 404 as Postgres, then waits on Docker that is already down.
Mitigation: Step 2b prints `@app.get("/ready` lines; 404 is path drift, not a compose up.
