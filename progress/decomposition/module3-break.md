# Module 3 BREAK — merchant account does not exist

Client has no Stripe account, no legal entity, no merchant paperwork. This is **not** “pick a different SDK.” They cannot legally take money. Code cannot create a business entity.

## Risk type

Does **not** fit integration/novelty/dependency/scale as taught — those are technical. This is **business/legal (organizational) risk**: conditions for the feature do not exist. Integration risk assumed a processor account. We were scoring the API; the missing condition is upstream of the API.

## What happens to the plan

W7/W8/W12 cannot become production tickets until legal says go. They stay **blocked externally**, like U-F8 was blocked on a PM policy. I will not “build our own processor” or swap brands to fake progress.

## Progress while payments are blocked

Yes. W1, W2, W4, W6, W12a, W3, W5, W9 still ship. Booking records `payment_status=blocked_merchant`. A **test-mode spike** still answers technical questions on a sandbox **only if** we treat it as scouting, not go-live. The **critical path to a paid booking** now includes an external milestone: merchant paperwork. The **critical path to a bookable marketplace demo** does not.

Plan around, do not solve the law.
