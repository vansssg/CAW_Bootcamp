# Module 3 DECIDE

## Decision 1 — risk framework: keep the four types

`decisions.module_03.risk_framework = integration | novelty | dependency | scale` (as taught)

Overlap is normal: **slot lock** is novelty (concurrency) + dependency (booking sits on it) + scale (thousands of concurrent books). Label all that apply; the highest one drives order.

Hardest to estimate: **integration** (Stripe/webhooks) — the other side can change. Personally: Redis-down jobs in System Design M07 was integration risk we treated as novelty and paid for with an in-process queue.

## Decision 2 — first build: **A spike first**

`first_build_target = spike`

Stripe + BLOCKED refund clocks: 2-hour test charge/refund in test mode answers “can Option 1 even be implemented?” before W8 production. Cost 2 hours vs six-week cancel rebuild.

Would pick B for schema-only risk (cannot spike a lasting model in 2 hours). Payments are not that case.

Middle ground later: keep the Stripe client wrapper if the spike succeeds; still throw away the script UI.
