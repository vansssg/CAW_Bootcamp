# AI-Augmented Engineering Module 05 REFLECT

## Iteration efficiency

Used 4 of 4. No restart — right call: the bus was structural 4 from round 1. Trajectory: 4/3 → 4/4 → 4/4 then a delivery regression in BREAK, then FIX restored 4/4. Shipped structural 4 / surface 4. Good enough to ship on this memory-backed shortener; not a 30s live heartbeat timer (constants only, no httpx client).

## Decision quality

Refine vs restart: keep the Queue writer, drop the close-after-first. Hindsight: same. Recognized the spiral when BREAK described silent drop after first event — matched `DROP_AFTER_FIRST_EVENT`. Surface vs structural: the close was a surface regression on a sound bus; confidence matched.

## Strategy (A refine-first)

Worked: invitations and the activity bus matched existing FastAPI/memory patterns. Restart-early would have rebuilt pub/sub to “fix” a one-line close. The failure mode of A showed up as Round 3 overwriting Round 1 connection stability — that is why the FIX prompt named the writer only.

## Decision callback (A)

The silent drop is refine-first’s cost: we kept iterating in the same file until heartbeat/reconnect logic closed after the first dispatch. A checklist that says “after this prompt, two events still arrive” would have caught it without a full restart.

## Knowledge

1. Iterate when structure holds; restart when the approach is wrong. Two failed refinements is the stop.
2. Biggest decision: A refine-first — saved the bus; FIX was one writer loop.
3. Proof: VERIFY_WS_ACCEPT, live event, cleanup, reconnect id 2; FIX_BOTH_EVENTS True.

Risk: another “helpful” close in a later prompt. Mitigation: two-event probe in CI next to module09.
