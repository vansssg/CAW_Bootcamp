# Module 03 BREAK — gaps in Jamie’s Kafka design doc

## Gap 1 — Missing Alternatives section (entire section absent)
**What goes wrong if approved:** Team rubber-stamps Kafka without comparing SQS/PubSub/outbox+worker. Infra cost, ops skill, and multi-tenant blast radius never debated. Same class of miss as building WebSockets without asking load-balancer owners.

## Gap 2 — Unvalidated capacity claim stated as fact
**Claim:** “analytics database … capacity for 10,000 writes/second” / “plenty of headroom” at 2k events/s peak.  
**What goes wrong:** If the “benchmark” was synthetic, single-row, or wrong shape (analytics bulk vs many small writes), cutover melts the DB. No open question, no load-test ticket, no cite.

## Gap 3 — Vague risk mitigations (not 3 AM actionable)
- “Monitor consumer lag closely and scale up if needed” — no alert threshold, no runbook, no max partitions/consumers, no page who.  
- Kafka down → “replication factor 3” does not cover producer behavior when cluster unavailable (buffer? fail request? drop?). Events still lost if publish fails after RF config.  
**What goes wrong:** On-call cannot execute; silent lag or silent drop.

## Also weak (honorable mention)
No Open Questions section; no “risk of doing nothing” vs cost of Kafka ops.
