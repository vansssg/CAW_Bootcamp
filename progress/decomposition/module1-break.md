# Module 1 BREAK — spec fights itself

## The contradiction

Original P1: cancel **with the provider’s cancellation policy applied** (P-F4 / U-F8).  
Ops “clarification” to P1: **platform-global** rule — full refund if cancel within 24 hours of **booking** (not of the appointment), else non-refundable. No exceptions.

These cannot both be true. If a provider’s policy is “full refund until 48h before the session, 50% until 24h before, else none,” then:

- A cancel 10 hours after booking, 3 days before the session: platform says **full refund**; provider says **full refund** (aligned).
- A cancel 2 days after booking, 10 hours before the session: platform says **non-refundable** (clock started at booking); provider says **50% or full** depending on their session-relative clock.

Even the **clock** differs: 24h from *booking* vs typical marketplace 24h from *appointment*. The clarification never revoked P-F4.

## What actually applies? (unanswered)

1. Does the platform rule override provider policy?
2. Does provider policy override, making the 24h rule a default?
3. Does the learner get the **more generous** of the two?
4. Is “within 24 hours of booking” a mis-edit that meant “within 24 hours of the appointment”?

## Why this is realistic

Ops wrote a consistent UX. Providers were sold autonomy in P2. Nobody merged the sections. Same failure class as CONTEXT (“cancel bookings” with no refund model) — now two refund models.

I will not pick a winner in BREAK. FIX must ask the PM which system is source of truth and mark the other revoked.
