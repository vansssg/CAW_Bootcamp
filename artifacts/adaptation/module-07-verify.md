# Module 07 VERIFY walkthrough

## Impact statement check (PM)
From `module-07-adaptation-note.md`:
- **Getting:** individual book + Meridian book-on-behalf (name/email)
- **Giving up:** org RBAC, company invoice, self-service listing, live Stripe, search/ratings, email
- **Next action for PM:** Meridian IT intro + OK that invoicing waits

All three clear → keep as written.

## Cut walkthrough (example: provider self-service / Slice 3)
- **Why cut:** seed providers already power browse/book; Meridian path does not need providers to edit listings in 6 days.
- **Depends on it:** Slice 4 reliability / Slice 3 tickets — none are MUST SHIP for demo.
- **What depended on it:** nothing in T1–T5 critical path; T4 books seeded slots.
- **Not cut blindly:** T4 kept (MUST); cutting T4 would break demo.

Other cuts (Stripe live, email, org RBAC) have seeded/sim/offline substitutes named in the note.

## Highest-impact blast row
**Booking flow API — MAJOR**
- Arrive at MAJOR: new required fields when flag true, validation branches, response shape, contract amend — > half day, not a one-line tweak.
- Confidence: **high** on API surface; **medium** on UI time (hence curl fallback risk).
- Might be wrong: if Meridian demands org invoice in-demo, payment/billing jumps from NO IMPACT → BLOCKED (would force replan).

## Anti-red-flags
- Did **not** keep everything / work harder — explicit CUT list.
- Did **not** restart — preserved T1–T3/T5 and Module 06 contracts; patched T4/T5/T6 + T7–T10.
