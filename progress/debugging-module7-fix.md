# Debugging Module 07 FIX

Checked BREAK critique against the lesson list: blame (John ×6), symptom-as-root-cause, person-actions as factors, vague impact, vague remediations, imprecise timeline. All were in `progress/debugging-module7-break.md`.

## Rewrite of the fictional migration postmortem

Did **not** invent user counts or UTC times the original omitted. Unknowns stay unknown.

### Root cause (system, not a person)

The deployment pipeline applies schema migrations to production without requiring them to pass against a staging database with production-like row counts. Dropping an index on `users` made login queries time out. A local test on a tiny dataset would not have caught that; “did not test” is a symptom. The control that should have blocked the apply is the pipeline, not an individual.

### Contributing factors (system gaps)

1. **CI has no migration dry-run.** There is no job that applies the migration to a clone and runs the login query with a latency budget.
2. **Review is optional on migration paths.** There is no CODEOWNERS / required-review rule on `**/migrations/**`. “Busy” is not a control.
3. **No post-migrate canary.** Detection was user reports. Query p99 / login error rate was not an apply gate.
4. **No weekend change freeze with a tested rollback.** “Rush” is a schedule gap, not a personality.

### Impact (honest)

- Count of affected logins: **unknown** (original: “some users”).
- Duration: **unknown** (original: Friday evening reports → Saturday morning rollback; no start/end UTC).
- Technical: index on `users` dropped; queries timed out; rollback restored the index (original does not prove login 200s after rollback).

### Remediations (specific, owned, dated)

Assume “today” is 2026-08-17 for deadlines (this workspace date), not “immediately / next week / ongoing.”

| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | CI job: apply pending migrations to a staging DB restored from a production-sized anonymized snapshot; fail if `GET /login` p99 > 200ms or HTTP 5xx | Platform | 2026-08-24 | Open |
| 2 | CODEOWNERS: `**/migrations/**` requires one `@db-owners` review; merge blocked otherwise | Engineering manager | 2026-08-24 | Open |
| 3 | Alert: login 5xx > 1% for 2m OR users-table sequential scan in `pg_stat_statements` after a migration; page on-call. Do not rely on user tweets | SRE | 2026-08-31 | Open |
| 4 | Document change freeze Fri 16:00–Mon 10:00 local **or** require the CI job in (1) green on the same SHA. “Try to avoid Fridays” is not a policy | SRE | 2026-08-24 | Open |
| 5 | Rollback runbook: restore dropped index, then `curl -sS -o /dev/null -w "%{http_code}" $BASE/login` must be 200 before closing the incident | Backend | 2026-08-24 | Open |

No “John.” No “be more careful.” No “try to.”

## Blind spots in our Module 07 postmortem

The fictional “John tested locally on small data” maps to us: recreate doubling was proven on the in-process `_local` map because Redis is down. A shared Redis prefix could still ship. The PR checkbox is the same class as “developers should test” — a human, not a merge block.

Edits applied to `progress/debugging-module7-postmortem.md`: contributing factor 6 (Redis-backed contract untested); remediation 1 requires a Redis service in CI, not only `_local`; remediation 5 is CODEOWNERS on contract files, not a self-checkbox; `cache_sot_mismatch` added to the alert item.
