# Module 3 VERIFY

## First three items — what we learn

1. **W1 Auth** — We have identity. Risk retired: almost none (libraries). Dependency retired: W6/W7 can start. Foundational ≠ risky.
2. **W2 Listings + pending + city** — We know the profile/slot parent row and that 5-city is a field, not a rewrite. Scale risk partly retired.
3. **W7 payment spike** — We know whether the processor can charge and refund on the cancel clock. **Biggest unknown retired.** If it fails, we have not built search/reviews/admin.

After item 3: “I know whether payments fit our booking/refund model. If yes, the rest is mostly known territory.”

If **item 1** fails on day 2: we wasted a day of auth, not a pipeline. If we saved payments for day 30: we waste the UI stack (oil well / 100 req/h story).

## Auth probe

Auth is **item 1**, not because it is scary: score 2, type dependency. High fan-out, low surprise. Payments are item 3 because they are high surprise. Did not put auth in top-3 uncertainty.

Risk = chance of surprise. Dependency = how many nodes wait.

## Bottom 3 hidden risk?

W10 notifications: integration with an email vendor — could bounce/spam; still soft (booking works). W12b “analytics on everything” is a scope bomb but not a product-killer. W9 reviews: still 1.

## Demo of 5

W1, W2, W7 spike, W4 slots, W6 booking — a learner can register, see a listing, lock a slot, book. Matches the top of the order (search/admin left out — Healthcare.gov).

## Spike placement

The 2-hour scout **is item 3** (W7), immediately before any W8 production ticket. Most valuable scout in the plan.
