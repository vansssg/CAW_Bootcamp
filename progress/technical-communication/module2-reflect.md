# Module 2 REFLECT

## Decision callback (chose A top_down)

I chose to lead with the answer. The BREAK memo is the opposite: GraphQL appears in paragraph 4 after ~220 words of throat-clearing. Anyone who stopped early had context and no conclusion — the Knight Capital runbook. Buried lede is the failure of the choice I did not make.

## Structure decision

- **Who:** Priya, new backend engineer, plus a skimming VP.
- **How they read:** 30-second headings + first sentences; 10-minute full read.
- **Opposite audience:** An exec still wants top-down. A controversial RFC for skeptical seniors might earn a short bottom-up “why now” after the lede, not instead of it.
- **Same choice again:** Yes. Sentence one of `technical-explanation.md` and of the FIX rewrite both survive alone.

## Principle to carry

Action items always name who is doing it. “Risks will be monitored closely” became “The backend team will track query latency daily for two weeks.”

## Biggest surprise

Passive voice hides in plain sight (`has been allocated`, `it has been observed`). Once tagged, the rewrite was mechanical. Seeing the buried lede was the hard skill.

## Ticket / acceptance

Goal: 1-page explanation without follow-up. First two sentences of BUILD:

> We are migrating ShopStream’s public API from REST to GraphQL over eight weeks so web and mobile can ask for exactly the fields they need. That cut should drop frontend API calls by about 40% and let us delete 15 one-screen aggregation endpoints.

Priya can tell a colleague the decision from those two lines. Criteria hit.

## Knowledge check

1. Core problem: correct facts in unscannable prose (buried lede, jargon, ownerless passives) so the reader cannot act under time pressure.
2. Biggest-impact decision: top-down lede. Everything else is wasted if paragraph 4 holds the action.
3. Evidence: BUILD lede + FIX 238-word rewrite with GraphQL in sentence one vs BREAK paragraph 4.

## Mini practical (VERIFY headline)

Opening two sentences: quoted above. Defined term: “GraphQL is a query language for APIs.” Next step: “Monday standup | Priya + migration trio | Priya has a schema slice and a buddy name.”

## Risk / mitigation

Risk: dual-run GraphQL queries unbounded / cache miss vs REST URLs. Mitigation: depth limits + persisted queries; backend team tracks latency daily for two weeks.
