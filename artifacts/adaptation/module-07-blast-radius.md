# Module 07 — Blast Radius

**Inputs:** Module 05 tickets T1–T6 · Module 06 contracts/plan · DECIDE B minimal company bridge  
**Replan style applied:** Preserve and Patch (Decision 2)

## Change 1: Company accounts (Meridian)

| Artifact | Status | Impact |
|----------|--------|--------|
| User data model | MINOR | Add `company_name TEXT NULL`, `can_book_for_others BOOLEAN NOT NULL DEFAULT false` on `users`. No Organization entity. |
| Auth/JWT system | MINOR | Register/login responses include the two new fields; no new roles. Token still Bearer opaque/JWT as built. |
| Booking flow (API) | MAJOR | `POST /api/bookings`: when `can_book_for_others`, require `booked_for_name` + `booked_for_email`; persist columns; include in 201 body. Validation 400 if flag false but fields sent. |
| Booking flow (UI) | MAJOR | Extra “Who is this for?” fields when flag true; confirmation shows delegatee. |
| Provider dashboard | NO IMPACT | Providers still see booking time/learner; show `booked_for_name` as display-only later (post-demo). |
| Search/listing | NO IMPACT | Availability-on-listing not in Meridian ask; leave listing as Module 05/06. |
| Payment/billing | NO IMPACT (demo) | Billing stays on booking user; Meridian reimburses offline. No org invoice. |
| Interface contracts (M06) | MAJOR | Amend C2/booking contract: optional `booked_for_*`; document flag gate. S2 slots enum unchanged. |
| Tickets completed (T1 seed, simulated T2/T3/T5) | MINOR | T5 register schema + response; seed may set one Meridian demo user with flag true. |
| Tickets in progress | — | Treat T2/T3/T5 merges as preserved; patch schemas only. |
| Tickets not started (T4, T6) | MAJOR | T4/T6 absorb booked_for fields + auth flag checks before demo. |

## Change 2: Compressed timeline (6 days)

| Ticket | Category | Why |
|--------|----------|-----|
| T1 Seed | MUST SHIP | Demo needs providers/slots |
| T2 GET providers | MUST SHIP | Browse path |
| T3 GET slots | MUST SHIP | Pick Tuesday 2pm |
| T4 POST bookings (+ booked_for) | MUST SHIP | Core book + Meridian bridge |
| T5 Register (+ company fields) | MUST SHIP | Meridian demo user |
| T6 GET my bookings (owner list) | SHOULD SHIP | Nice confirmation history; survivable if confirmation page only shows 201 payload |
| Provider self-service listing (Slice 3) | CUT | Seeded providers enough for demo |
| Payments / Stripe live | CUT | Simulated confirmation OK if Stripe env slips |
| Search filters / ratings | CUT | Not required for Meridian book-on-behalf |
| Provider analytics | CUT | Zero demo impact |
| Proper Organization RBAC | CUT | Explicit post-deal debt from DECIDE B |
| Email notifications | CUT | On-screen confirmation sufficient |

Rule used: undecided → CUT.

---

## BREAK overlay — RBAC (update, not rewrite)

| Artifact | Updated status | Notes |
|----------|----------------|-------|
| Auth/JWT | **MAJOR** (was MINOR) | Role + department in session |
| User data model | **MAJOR** (was MINOR) | `org_role`, `department_id` |
| Booking API | **MAJOR** | + role checks on create/list |
| Booking list T6 | **MUST SHIP** (was SHOULD) | Visibility by role |
| Payment/billing | NO IMPACT | Still personal booker billing |
| Search/listing | NO IMPACT | Unchanged |
| Full Organization entity | Still CUT | Thin roles only for 6-day |

See `module-07-break-delta.md` for decision retract detail.
