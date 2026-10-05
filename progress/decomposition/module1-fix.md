# Module 1 FIX — two buildable cancellation policies

Contradiction: provider-owned policy vs platform 24h-from-booking refund. Junior move: “needs clarification.” Senior move: two implementable options with tradeoffs.

## Option 1 — Platform-first

Full refund if `canceled_at - booked_at < 24h`, else none. Providers cannot override. One checkout sentence. Refund job is one predicate. Same-day providers lose stricter policies.

## Option 2 — Provider policy + 1h floor

Always full refund in the first hour after booking. Then provider structured buckets vs appointment time. Must display at checkout. More code; both stakeholders served.

PM must pick one. Mixing is how we rebuild payments again.

## Document updates

- U-F8 and P-F4 flagged **BLOCKED — pending PM decision**
- Both options written in `module-01-requirements.md`
- Affected: U-F5 pay, O-F5/P-F6 earnings, O-Q2 testable cancel, P-F4 existence

## Tension spotted (not handed)

Provider calendar simplicity vs thousands of concurrent bookers on one slot → locking/versioning, not a yes/no spec bug.
