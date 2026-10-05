# Module 08 — Pre-integration contract check + big-bang merge log

**Mode:** standalone_simulated  
**Integration order:** big_bang (DECIDE A) — with bisect plan if smoke fails  
**Sources:** `module-06-interface-contracts.md`, `module-06-agent-output-bundle.md` (post-FIX), `module-07-updated-plan.md`

## Phase 1 — Contract check

| Seam | Sender → Receiver | Format | Path/method | Status/enums | Errors | Result |
|------|-------------------|--------|-------------|--------------|--------|--------|
| C1 list→slots | T2 `providers[].id` → T3 path | UUID OK | GET `/api/providers/{id}/slots` | n/a | 404 `provider_not_found` | PASS |
| C1 slots→book | T3 `slots[].id/status` → T4 | UUID; **`open`\|`booked`** (FIXED from `available`) | POST `/api/bookings` | open required | 409 `slot_unavailable` | PASS post-FIX |
| C2 auth→book | T5 `user.id` → T4/T6 `learner_id` | UUID OK | Bearer header | roles M07 | 401/403 | PASS thin roles |
| Datetimes | all | ISO-8601 `Z` string (not Unix) | — | — | — | PASS |
| Error envelope | all | `{error:{code,message}}` | — | — | no stack traces | PASS |
| Booking→notify (if any) | — | **N/A CUT** email | — | — | — | Deferred — no seam |

**Flagged pre-merge:** none remaining after Module 06 enum FIX.  
**Watch:** M07 `booked_for_*` only when `org_role=manager`.

## Phase 2 — Big-bang merge log

Merged in one shot: `agent/t2-providers` + `agent/t3-slots` (corrected) + `agent/t5-auth` (+ M07 role patches) onto integration branch `integrate/module-08`.

| Check | Result | Notes |
|-------|--------|-------|
| T2 AC in integrated env | PASS | 3 providers |
| T3 AC | PASS | status `open` |
| T5 AC | PASS | register + roles |
| Cross smoke: list→slots→register | PASS | |
| Cross smoke: manager book-for | PASS (sim) | booked_for fields |
| Employee book-for | PASS 403 | |
| Concurrent slot | PASS (sim) | one 201 one 409 |

**If big-bang had failed:** bisect order revert T5 → retest → revert T3 → retest → isolate seam.

## Handoffs (happy path)
Browse(T2) → slots(T3) → book(T4) → list(T6). Confirmation on-screen (email CUT).
