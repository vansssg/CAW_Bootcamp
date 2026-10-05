# Module 08 VERIFY

## User journey (search → booking) — no hand-wave

| Step | Component | Handoff | Data / format | If downstream down |
|------|-----------|---------|---------------|--------------------|
| 1 Browse | T2 GET `/api/providers` | FE → T2 | JSON providers UUID | — |
| 2 Pick provider | FE | T2.id → T3 path | UUID string | — |
| 3 List slots | T3 GET `/api/providers/{id}/slots` | FE → T3 | slots[].id UUID, status `open`, starts_at ISO `Z` | — |
| 4 Auth | T5 register/login | FE stores Bearer | token string; user.id UUID; org_role | booking 401 |
| 5 Book | T4 POST `/api/bookings` | FE → T4 | `{slot_id, booked_for_*?}` + Bearer; response booking id UUID, status `confirmed`, times ISO `Z` | — |
| 6 Confirm UI | FE | uses T4 201 body | same JSON | Email **CUT** — no notify seam; if notify existed would need ISO↔Unix contract (CONTEXT bug) |
| 7 List own | T6 GET `/api/bookings/me` | Bearer → T6 | filtered by role | — |

Exact contract match example (slots→book): sender `slots[].id` UUID + `status:"open"`; receiver requires `slot_id` UUID and open slot — **exact** after Module 06 FIX (was `available`).

## Non-Built audit (voluntary)
From matrix — not claiming full coverage:
- **Simplified:** U-F1/U-F2/P-F2/P-F3/O-C3 — conscious demo cuts
- **Deferred:** U-F3,U-F5,U-F6,U-F7, P-F1,P-F5–P-F8, O-F*, payments, email — on Module 07 CUT / post-deal tickets (T11)
- **Blocked:** U-F8, P-F4 — PM cancel policy
- **Lost:** none silent

O-F1 vetting: **Deferred** — seeded providers, no admin approve UI; dropped at Slice 1 anti-scope / M07 cut, not lost silently.
