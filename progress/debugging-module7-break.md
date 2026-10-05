# Debugging Module 07 BREAK — fictional migration postmortem

Fictional doc titled “Postmortem: Database Outage on March 15th.” Everything that can be wrong is wrong. Catalogued **before** the next section.

## 1. Blame (person as subject)

| Quote | Why it fails |
|-------|----------------|
| Root cause: “John deployed the broken migration…” | Subject is a person. A blameless rewrite names the pipeline. |
| “John did not test the migration locally.” | Same. The gap is “CI does not apply migrations to a clone and run the login query.” |
| “Nobody reviewed John's PR because everyone was busy.” | Busy people are not a control. Missing required review / CODEOWNERS is. |
| Remediation 2: “John will have all future PRs reviewed” | Punishes one engineer. Next hire repeats the outage. |
| Lesson: “John needs to be more careful.” | Explicit blame. Care is not a control. |

## 2. Timeline is not a timeline

- Title: “March 15th” — no year, no timezone.
- “Friday afternoon / evening / Saturday morning” — same class as “around midday.”
- No detection timestamp, no rollback timestamp, no “queries recovered” timestamp.
- Compare to our Module 07 postmortem: `2026-08-17 08:03:46.217Z` and PITR `2024-03-15 14:20 UTC`.

## 3. Impact is not quantified

“Some users could not log in for a while” answers none of: how many users, what % of logins, duration in minutes, which region, data loss yes/no.

## 4. Remediations change humans, not systems

| # | Item | Failure |
|---|------|---------|
| 1 | “Developers should test migrations before deploying” | Same as “be more careful.” No script, no CI job, no staging apply. A new engineer cannot execute this without asking “how?” |
| 2 | “John will have all future PRs reviewed” | Person-specific. Does not add a required reviewer on `**/migrations/**`. |
| 3 | “Try to avoid deploying on Fridays” | Superstition. An untested index drop on Monday has the same blast radius. “Try” / “Everyone” / “Ongoing” is not a deadline. |

Deadlines “Immediately / Next week / Ongoing” are not dates.

## 5. Incident report wearing postmortem clothes

- Summary: “The database went down on Friday afternoon.” No SEV, no user count.
- Resolution: “We rolled back the migration.” No proof login recovered (no status code, no p99).
- No “what we still do not know.”
- Technical fact (dropped index on `users` → timeouts) is useful but buried under John’s name.

## 6. Detection and monitoring missing

Outage discovered by “users reported errors.” No alert on login p99, no migration-apply canary, no “index missing” check. That is a contributing factor the doc never names.

## 7. Wrong lesson (Friday deploys)

“We should not deploy on Fridays” does not prevent the class. The class is **schema changes without a test that would fail if `users` login queries sequential-scan.** Friday is correlative, not causal.

## 8. Owners are not accountable roles

“All developers,” “John’s manager,” “Everyone” — nobody can close the ticket. Contrast: our remediations name Platform, SRE, Backend, Engineering manager with `2026-08-24` / `2026-08-31`.

## Count

**16 distinct problems** in eight groups: blame (5 quotes), imprecise timeline, unquantified impact, three vague remediations + fake deadlines, no verification of rollback, no unknowns, missing detection/monitoring, Friday myth, non-owners.

Did not rewrite the fictional doc in this step (FIX). Did not invent timestamps for their outage.
