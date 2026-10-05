# SkillSwap requirements matrix (Module 01)

Product: SkillSwap (`bootcamp.product_scenario = skillswap`).  
Structure: DECIDE B — stakeholder × type.  
Spec source: BUILD verb/qualifier/silence passes (the three-paragraph spec was referenced by paragraph, not inlined in the CLI payload). I did not invent extra product features beyond those passes and the CONTEXT cancel story.

Types: F = functional, C = constraint, Q = quality attribute.  
Source: P1/P2/P3 = paragraph; E = explicit; I = implicit.

## USER (learner)

| ID | Requirement | Type | Source | Confidence |
|----|-------------|------|--------|------------|
| U-F1 | Browse providers by category | F | P1 E | high |
| U-F2 | View provider profiles | F | P1 E | high |
| U-F3 | See ratings on profiles | F | P1 E | high |
| U-F4 | Book a time slot | F | P1 E | high |
| U-F5 | Pay through the platform at booking | F | P1 E | high |
| U-F6 | Receive a confirmation email after booking | F | P1 E | high |
| U-F7 | Cancel a booking | F | P1 E | high |
| U-F8 | **BLOCKED — pending PM decision.** Cancellation refund rule. Original: provider policy applies. Ops update: full refund within 24h of booking, else none. See Cancellation decision. | F | P1 conflict | blocked |
| U-Q1 | Search must feel instant | Q | P1 E | medium (no SLA number) |
| U-C1 | Cannot double-book the same slot (two learners, one slot) | C | P1 I + skill constraint | medium |

## PROVIDER

| ID | Requirement | Type | Source | Confidence |
|----|-------------|------|--------|------------|
| P-F1 | Set own availability | F | P2 E | high |
| P-F2 | Set own pricing | F | P2 E | high |
| P-F3 | Set own service descriptions | F | P2 E | high |
| P-F4 | **BLOCKED — pending PM decision.** Set own cancellation policy (dead if Option 1 wins). | F | P1 E / P2 I | blocked |
| P-F5 | See own bookings | F | P2 E | high |
| P-F6 | See own earnings | F | P2 E | high |
| P-F7 | See own reviews | F | P2 E | high |
| P-F8 | Flag a learner as no-show | F | P2 E | high |
| P-Q1 | Dashboard remains usable at “a few thousand users” city scale | Q | P3 I | low |
| P-C1 | Pricing/availability autonomy is within platform limits (unstated) | C | P2 qualifier “their own” | low |

## PLATFORM / OPS

| ID | Requirement | Type | Source | Confidence |
|----|-------------|------|--------|------------|
| O-F1 | Vet / approve new providers | F | P2–P3 E | high |
| O-F2 | Resolve disputes | F | P3 E | high |
| O-F3 | Handle escalated disputes | F | P3 E | high |
| O-F4 | Analytics that track marketplace activity | F | P3 E | medium (“everything”) |
| O-F5 | Compute payout as price minus platform commission | F | P2 I | medium |
| O-C1 | Platform commission is 15% of earnings | C | P2 E | high |
| O-C2 | Launch supports at least a few thousand users | C | P3 E | medium (“a few”) |
| O-C3 | Expand to 5 cities within 6 months without a full rebuild | C | P3 E + skill constraint | high |
| O-Q1 | Observability sufficient for “analytics on everything” | Q | P3 E | low (scope of “everything”) |
| O-Q2 | Slot conflict checks are testable (no silent overwrite) | Q | skill constraint I | medium |

Count: 25 distinct rows (≥15).

## Cancellation decision (BREAK/FIX)

Two systems cannot both ship. **U-F8 and P-F4 are BLOCKED** until the PM picks one option.

### Option 1 — Platform-first (ops clock)

Rule: full refund if the learner cancels within 24 hours **of the booking timestamp**; after that, $0 refund. Providers cannot override. Checkout shows one sentence of policy.

Affects: learner UX is one rule; same-day tutors cannot set “non-refundable after book.” Simpler refund job: one if-statement on `now - booked_at`.

Tradeoff: consistent UX vs provider autonomy (P-F4 dies).

### Option 2 — Provider policy with a 1-hour platform floor

Rule: always full refund if cancel within 1 hour of booking (cooling-off). After that, the provider’s **structured** policy vs **appointment** time applies (e.g. 100% / 50% / 0% buckets). Policy JSON is shown before pay.

Affects: more build (policy editor, checkout copy, refund calculator). Serves both stakeholders.

Tradeoff: autonomy + safety net vs complexity.

I am not choosing for the PM. Either option is buildable; mixing them is not.

### Other rows this decision touches

- U-F5 pay-through-platform: hold vs capture (CONTEXT). Option 1 is easier with capture-on-book plus refunds in 24h; Option 2 needs capture timing aligned to buckets.
- O-F5 / P-F6 earnings: refunds reverse commission; dashboard must not show refunded gross as take-home.
- P-F4: exists only under Option 2.
- O-Q2 testable cancellation: free-text policy is not testable; Option 2 requires structured buckets.

## Tension (not a binary contradiction)

P-F1 “providers set their own availability” wants a simple calendar. O-C2 “a few thousand users” implies concurrent book of the same slot. Autonomy vs race: we need a lock or version on the slot row (SkillSwap no-double-book). Design choice, not a spec typo.

## Ambiguities and open questions (ask the PM)

1. Does the 15% commission apply to all categories, or can it vary? (O-C1)
2. What is “feel instant” in milliseconds, and at what concurrent search QPS? (U-Q1)
3. Is payment authorize-and-capture at book, or hold until session start? This decides refunds under P-F4 / U-F8 (CONTEXT six-week failure).
4. Who may rate whom, and only after completed sessions? (U-F3)
5. Are learner and provider separate accounts, or can one person be both? (silence: auth)
6. When and how does the provider receive the remaining 85%? (silence: payout)
7. What is a city (dropdown vs geofence) and which timezone is shown on a slot? (silence: city/TZ)
8. Is cancellation policy structured rules (e.g. full refund if ≥24h) or free text? Unstructured text is not testable (skill constraint).
9. What is vetting: ID/license docs, background check, description review, interview? Manual or automated? Can a rejected provider reapply? (O-F1 is a feature at zero depth.)
10. What does “analytics on everything” include: page views, booking funnel, revenue by city, cohorts? Real-time vs batch? (O-Q1 — “everything” is a 50-page spec hiding in one word.)

## Notable silences (not requirements until the PM answers)

Auth/signup, web vs mobile, SMS/push, payout rail, city model, category ownership, structured cancel rules, two-way ratings, timezone, i18n/currency.
