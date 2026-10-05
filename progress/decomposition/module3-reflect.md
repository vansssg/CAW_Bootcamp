# Module 3 REFLECT

Before: risk meant “hard.” Now: integration / novelty / dependency / scale, plus **business/legal** after BREAK. Auth is high-dependency low-risk; Stripe was high-integration until we learned there is no account.

Most likely to underestimate: **business/legal** — I scored payments as API risk; the missing merchant entity was upstream. Same class as Redis-down treated as a code problem.

Surprise: the blocker was not which SDK. A 2-hour technical spike (DECIDE A) would have produced test-mode code and still missed “no entity.” Scouting the code does not scout the organization.

Tomorrow, first: name the biggest unknown and the **preconditions** (account, policy, legal), then a spike only for the technical slice.

## Knowledge

1. Core problem: comfortable-first hides whether the product is even possible (oil well / payments).
2. Biggest decision: spike-first + four types — then adapting when the type was legal.
3. Evidence: `risk-plan-module-03.md` scores, stub contract, PM two-liner, W8 blocked not deleted.

## Mini practical

VERIFY: after items 1–3 we know identity, listing/city/pending, and (originally) payment scout. Auth not in top-3 uncertainty.

## Risk / mitigation

Risk: team idles on legal. Mitigation: stub `processPayment`; escalate merchant date; W4/W5 continue.
