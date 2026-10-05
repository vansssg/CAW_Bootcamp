# Module 2 BREAK — ShopStream “accurate but unreadable” memo

Facts are right. Writing works against Priya. Count below is **22** tagged problems (well above the “look again if < 10” bar).

## Buried lede

1. **Where is the decision?** Paragraph 4: “the team has decided to migrate from REST to GraphQL.” Reader wades through **three paragraphs / ~220 words** of throat-clearing first. A VP who stops at paragraph two never learns GraphQL.

2. Opening sentence answers nothing: “evaluating several potential approaches to addressing some of the challenges…” — Check 1 weak lede.

## Structure

3. **No headings.** Cannot skim. Knight Capital failure mode.

4. **No bullets.** 47 endpoints, 15 aggregations, 8 weeks, 40%, three engineers are buried in sentences.

5. **No next-steps section.** Document dies on “timeline is subject to adjustment.” Priya does not know what to do Monday.

6. **SDK versioning and SRE latency** appear in paragraph 3 with no heading, so they compete with the migration decision.

## Passive voice (actor hidden)

Quoted; owner missing unless noted.

7. “a decision has been reached” — by whom?
8. “It should be noted that the existing system… has presented certain inefficiencies that have been identified” — identified by whom?
9. “significant sprint capacity is consumed by the creation…” — FE team is named nearby but the verb is still passive.
10. “it has been observed that BFF patterns were considered… but were ultimately deemed”
11. “Different data shapes are required by the mobile and web clients”
12. “backwards compatibility has been difficult to maintain”
13. “multiple sequential REST calls are being made by the mobile app”
14. “Three engineers have been allocated”
15. “which has been identified as a risk that will be mitigated”
16. “The REST API and GraphQL endpoint will be operated simultaneously”
17. “it has been acknowledged that query performance…”
18. “These risks will be monitored closely and addressed as they arise” — by whom, how, what is “closely”? (also **ambiguity**)

## Jargon without definition

19. **REST, GraphQL, endpoints** used as if Priya already lives here (contrast: our BUILD defined buffet vs fixed menu).
20. **BFF** never expanded or analogized.
21. **FE, SDK, SRE** as unexplained team codes.
22. **aggregation endpoints**, **API versioning**, **query performance unpredictability**, **caching complexity** — no one-sentence meaning.

## Wordiness

23. “As many of you are aware” — empty.
24. “After extensive deliberation and analysis of various factors including…” — could be “We compared velocity, client latency, and maintainability.”
25. “It should be noted that” (twice) — delete.
26. “what are essentially the same underlying data entities, resulting in the proliferation of purpose-built endpoints that must be individually maintained, tested, and monitored” — “web and mobile want different JSON for the same objects, so we grew 15 one-screen routes.”

## Ambiguity

27. “timeline is subject to adjustment based on findings” — who decides, what finding slips the date, who tells Priya?
28. “Stakeholders should be aware” — which stakeholders? Priya is not a stakeholder; she is the new engineer who needs work.

(Items 18 and 27–28 overlap categories; unique issues still **> 10** even if overlap is collapsed.)

## What I should notice

This is normal untaught engineering prose: smart author, correct facts, reader loses. The migration sentence in paragraph 4 is the Knight Capital runbook: the action exists and is late.
