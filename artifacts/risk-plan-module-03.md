# SkillSwap risk plan — Module 03

Framework: integration | novelty | dependency | scale.  
First-build: **spike** on payment (DECIDE A). DAG: `artifacts/dag-module-02.md`.

## Part 1 — node annotations

| ID | Item | Score | Types | Notes |
|----|------|------:|-------|-------|
| W1 | Auth | 2 | Dependency | Libraries exist; almost everything needs who. **Not** top-3 uncertainty. |
| W2 | Listings + city + pending | 3 | Dependency, Scale | Pending vs live (cycle fix). City field now so 5-city is not a rewrite. |
| W3 | Onboarding | 3 | Novelty | States: pending/approved/rejected via W12a. |
| W4 | Slot lock | 4 | Novelty, Scale | Two learners, one slot. Race. |
| W5 | Search | 3 | Scale | Instant is a wish until SLA; **not** first. |
| W6 | Booking | 3 | Dependency | Needs W1+W2+W4. Medium once slots exist. |
| W7 | Payment **interface** + spike | 5 | Integration | External processor, webhooks, 15%, refund clocks. Scout in hours. |
| W8 | Payment implementation | 4 | Integration | Production after spike. |
| W9 | Reviews | 1 | — | CRUD. Tedious ≠ risky. |
| W10 | Notifications | 2 | Integration | Email vendor, but booking works without it (soft). |
| W11 | Cancel **policy contract** | 5 | Integration, Dependency | BLOCKED Option 1 vs 2. Invalidates W12 if wrong. |
| W12 | Refund flow | 4 | Integration | Depends on W11 + payment iface. |
| W12a | Minimal review tool | 2 | Novelty | `approve id`; small. |
| W12b | Full admin | 2 | Scale | Analytics “everything”; slack. |

**Top 3 uncertainty (not auth):** W7 spike/payments (5), W11 cancel contract (5), W4 slot lock (4).

## Part 2 — build order (risk early, hard edges honored)

1. **W1 Auth** (2, dependency) — Unblocks W6/W7. Low uncertainty, high fan-out. Not because it is scary.
2. **W2 Listings + pending + city** (3, dep+scale) — Unblocks slots, search, W12a. City now = cheaper than migrate later.
3. **W7 Payment interface + 2h spike** (5, integration) — First high-risk after W1. Throwaway: can we authorize and refund on the Option-1 clock in test mode? If no, stop UI sprawl.
4. **W4 Slot lock** (4, novelty) — After W2. Second unknown. Do not wait for search.
5. **W12a Minimal review** (2) — After W2 pending rows. Unblocks W3; breaks the admin cycle. Parallel with W4.
6. **W3 Onboarding** (3) — After W12a.
7. **W6 Booking** (3) — After W1+W2+W4 (hard). Now the payment spike already answered “can we charge.”
8. **W11 Cancel contract** (5) — After W6 timestamps exist. PM must pick Option 1 or 2 **before** W12. Same week as W6 if the spike informed the clock.
9. **W8 Payment implementation** (4) — After W6+W7. Real ticket only if spike passed.
10. **W12 Refund flow** (4) — After W11+W7 (W8 soft).
11. **W5 Search** (3, scale) — After W2; **late** so we do not repeat search-without-model / Healthcare.gov dashboards-first.
12. **W9 Reviews, W10 Notify, W12b Full admin** (1–2) — Endpoints; slack. Comfortable work last.

Justifications are risk-vs-DAG, not “felt right.” CRUD never scored high because of field count.

## FIX — merchant paperwork is a business blocker

Truly blocked: live money movement, processor account, real commission, real refunds.  
Not blocked: `processPayment` contract, transaction rows, price UI.

Stub (dev):

`processPayment(booking_id, amount, method) → { status: success | failed, transaction_id }`

Always `success` in local/dev. Booking talks to the contract, not a vendor.

### PM message (two sentences)

Payment processing is blocked — the client has no merchant entity or processor account, so we cannot legally move money. We are stubbing `processPayment` so booking/slots continue, and we need a date when a test merchant account exists; until then live payment testing is off the calendar.

### Revised build order

1. W1 Auth  
2. W2 Listings + pending + city *(scale risk moves up)*  
3. **W7 Payment interface + stub** (not a live processor)  
4. W4 Slot lock *(novelty — team bandwidth while legal is blocked)*  
5. W12a Minimal review  
6. W3 Onboarding  
7. W6 Booking against the stub  
8. W11 Cancel contract (policy still BLOCKED on PM, independent of merchant)  
9. W5 Search  
10. W9 Reviews, W10 Notify, W12b Full admin  
11. **W8 Payment integration — BLOCKED waiting on client merchant account** (returns to top of queue the day legal clears)  
12. W12 Refund implementation — blocked on W8 + W11  

Team does **not** wait. When legal clears, W8 jumps the queue; stub swaps for the real adapter behind the same contract.
