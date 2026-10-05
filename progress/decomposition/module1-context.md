# Module 1 CONTEXT — requirements hide questions

The six-week cancellation build failed because “Users should be able to cancel bookings” hid: when, refund, who owns policy, what happens to the slot. Code was fine. Requirements were not.

Same pattern for SkillSwap sentence: **“Users can book time slots and pay through the platform.”**

## Assumptions I found (before reading the hint list)

1. **User** = learner, not provider or admin. Guest vs logged-in vs verified-ID is unstated.
2. **Time slot** identity: timezone of provider vs learner; DST; overlapping services.
3. **Double-book:** last-write-wins vs lock vs waitlist — SkillSwap constraint says conflicts must prevent double-booking, but this sentence does not say how.
4. **Pay** = authorize-and-capture now vs hold-then-capture after the session (the cancellation story’s real cost).
5. **Commission:** platform take is a SkillSwap constraint but this sentence never mentions it — payout vs pass-through.
6. **Currency / city:** one city now vs multi-city later (another SkillSwap constraint) — tax, FX, local hours.
7. **Failure:** payment fails after reserve — slot released immediately or held?
8. **Confirmation:** auto-confirm on pay vs provider must accept (the “provider unavailable calendar” case).
9. **Idempotency:** double-click pay — one booking or two charges?
10. **Cancellation coupling:** booking+pay without a cancel/refund contract repeats the six-week story.

## Hint list (also true)

Slot duration min/max; book vs hold; two users same slot; payment methods; guest browse; real-time vs provider confirm.

Twelve words, ≥10 unstated decisions. Module 1 skill: find the questions before anyone writes a booking table.
