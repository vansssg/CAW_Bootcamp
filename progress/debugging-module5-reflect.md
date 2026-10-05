# Module 05 REFLECT

## 1) Triage decision and evidence
- Severity selected: **SEV1**.
- Evidence used:
  - alert described **47 DELETE requests** to admin endpoint from unrecognized IP in 10 minutes,
  - requests returned **HTTP 200** (successful, not blocked),
  - auth header anomaly (`present but empty`) suggested auth-path exploitability.
- Would not downgrade now: BREAK stage confirmed real impact (12 deleted rows across 8 user accounts), which validates the original SEV1 classification.

## 2) Hardest communication moment
- Hardest point: second VP pressure message asking for reassurance that this was not a breach.
- Why hard: competing incentives between truthfulness and stakeholder anxiety reduction.
- Why not downplay: saying "not a breach" would create an inaccurate executive narrative and amplify trust damage once deletion impact surfaced.

## 3) Debugging vs communication tradeoff
- Chosen strategy (from DECIDE): communicate first, then fix; cadence on state change.
- Tradeoff observed:
  - Pro: stakeholders received concrete updates tied to exploit scope and demo-impact boundaries.
  - Con: communication drafting consumes response time while exploit window may still be active.
- Practical rhythm used in this module: short, structured updates at state transitions (triage confirmed -> root cause isolated -> fix path defined -> post-fix loss discovered -> recovery plan).

## 4) One concrete thing to improve next time
- Improvement: send an immediate 60-second acknowledgment followed by a fixed template update including:
  - severity,
  - current impact count,
  - customer-facing blast radius,
  - next update SLA.
- This reduces ambiguity while preserving debugging focus.

## 5) Communication as incident response
- Agreed. Communication was not auxiliary; it constrained organizational behavior (demo decisions, executive escalation, stakeholder confidence) while technical remediation progressed.

## Knowledge check
1. Core module problem solved:
   - handling technical incident resolution and stakeholder communication concurrently under pressure.
2. Biggest-impact decision:
   - triage priority + communication cadence; these decisions determine both incident trust quality and exploit window management.
3. End-to-end evidence from this module:
   - build/verify artifacts and command outputs showing strict Authorization validation behavior for malformed inputs plus pass path for valid token.

## Mini practical task (STEP 4 style verification proof)
- Action performed: auth verification matrix for incident-path fix.
- Command outputs (recorded in `progress/debugging-module5-build.md` and `progress/debugging-module5-verify.md`):
  - empty -> `401 Authorization required`
  - whitespace -> `401 Authorization required`
  - bearer without token -> `401 Invalid authorization format`
  - wrong token -> `401 Invalid token`
  - valid token -> pass

## Concrete risk + mitigation
- Risk: exploit closure can mask unresolved business impact (data already deleted before patch).
- Mitigation: mandatory post-fix audit stage with row-level impact query, restoration plan (PITR/backups), and explicit stakeholder update on residual damage.

## Limitation disclosure
- Full DB-backed route/PITR execution could not be run in this environment due local DB connectivity constraints; this was documented in BREAK/FIX artifacts without fabricating completion.
