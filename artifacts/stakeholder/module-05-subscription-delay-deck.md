# Stakeholder deck: Subscription launch delay (security fix)

**Audience:** VP Product, Head of Marketing  
**Medium:** Visual presentation (DECIDE B) — max 6 slides + speaker notes  
**Leave-behind:** one-page PDF of these slides after the call

---

## Slide 1 — The ask (business first)

**Title:** We need to move the subscription launch by 3 weeks

**Bullets:**
- Original ship date → **+3 weeks**
- Reason: fix a **high-severity payment security hole** found in audit (not yet exploited)
- Same engineers cannot ship subscription features and the fix in parallel

**Speaker notes:** Open with the date change. Do not say “tokenization.” Pause. Confirm they heard the delay before diving into why.

---

## Slide 2 — What customers would feel if we ship anyway

**Title:** The risk if we launch on the old date

**Bullets:**
- Attackers could **reuse a “payment ticket stub”** to charge customers again
- Coat-check analogy: photocopied stub → pick up someone else’s coat (money)
- Rated **high** by Security; peers saw similar issues exploited within weeks of disclosure
- Brand + chargeback + trust hit during a brand-new subscription launch

**Speaker notes:** Analogy = coat check ticket photocopy. Emphasize “not exploited yet” is not “safe.” Marketing cares about launch-week trust.

---

## Slide 3 — What we’re doing

**Title:** Fix first, then launch

**Bullets:**
- ~**3 weeks** of eng work across **3 payment-related services**
- Blocks the reuse attack; keeps card numbers out of our systems (tokens stay)
- Subscription build resumes after the fix ships
- Maintenance/customer impact of the *fix* is low vs a public exploit during launch PR

**Speaker notes:** Translate: we change how we validate payment tickets so old stubs can’t be replayed. No deep architecture.

---

## Slide 4 — Tradeoff (visceral)

**Title:** On-time with an unlocked back door — or delay and lock it

**Analogy (on slide):**  
Launching subscriptions with this hole is like opening a new store for a grand opening while the **back door lock is broken**. No one has tried the handle yet. The ribbon-cutting crowd is the worst time to find out.

**Bullets:**
- Option A: ship on original date → marketing win, security debt on day one  
- Option B: delay 3 weeks → fix lock, then open the store  

**Speaker notes:** Ask which they’d pick for their own store. Don’t debate Redis.

---

## Slide 5 — What we need from you

**Title:** Decisions this week

**Ask (clear):**
1. **Approve** shifting subscription launch from **[original date]** to **[+3 weeks]**  
2. Marketing: **update** customer/board announcement calendar this week  
3. **Book 30 minutes Thursday** with Product + Marketing + Eng to lock external messaging (no panic language; honest “security hardening before launch”)

**Speaker notes:** Not “thoughts?” — need verbal yes on date + Thursday slot before leaving the room.

---

## Slide 6 — FAQ / expected pushback

**Title:** Anticipated questions

| If they ask… | You say… |
|--------------|----------|
| Can we launch and patch later? | Launch week is when attackers + press watch; patch-after burns trust twice |
| Can another team fix it? | Domain knowledge is on payments; handoff adds time, doesn’t save the calendar |
| Can we cut scope to save a week? | Security fix is the critical path; subscription polish can slip further if needed, not the fix |
| What do we tell the board? | “We delayed 3 weeks to close a high-severity payment flaw before taking subscription payments” |

**Speaker notes:** Offer the one-pager leave-behind. Confirm owners for board/customer copy.

---

## Parent-test (first paragraph / Slide 1)

“We need to delay the subscription launch by 3 weeks to fix a serious payment security issue before customers start paying us monthly.”
