# Module 3 CONTEXT — scary first

Easy-first (profiles, search CSS) feels productive. SkillSwap without payments is a brochure. Delay discovering Stripe/refunds fail and everything on W8/W12 is a dry well under a pipeline.

Oil well: test well before pipeline. Startup: 3 months of UI then third-party API at 100 req/h vs 10,000 needed.

## Rank (most → least risk)

1. **Stripe / payment API** — external, webhooks, idempotency, refunds vs BLOCKED U-F8. Highest unknowns. Maps to W7/W8.
2. **Provider profile schema** — we own it but indexes/pending-vs-live last (W2). Medium.
3. **CRUD profile form** — known pattern, easy to redo. Lowest. Time ≠ risk.

## Spike

Time-boxed throwaway that answers one question (e.g. “can we charge and refund a test booking in Stripe test mode in 4 hours?”). Not production. Buy information. Healthcare.gov analogue: one enrollment path before 55 dashboards.
