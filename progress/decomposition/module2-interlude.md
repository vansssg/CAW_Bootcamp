# Interlude — Healthcare.gov (2013)

1 Oct 2013: Healthcare.gov launch. ~$600M+, 55 contractors. Six successful enrollments on day one. Components worked in isolation. Session tokens and eligibility payloads did not match at boundaries. Load balancing was per-component. End-to-end testing was essentially launch day.

Rescue (“tech surge”) did not open a bug pile first. They **mapped** identity → eligibility → plan compare → enroll → pay, found the **critical path** (thinnest path to one enrollment), stabilized that, then expanded. By end of open enrollment, 8M+ signups.

## 1. Why 55 plans were not enough

Each plan described one team’s interior. Missing: a **cross-contractor DAG** of interfaces — data formats, error codes, what happens when identity is slow. Same hole as SkillSwap if W7 payment iface is not written down: W8 and W12 each “work” and refunds still disagree. Connections, not parts, are what failed.

## 2. Day-2 first action

Draw the whole-system graph and the **thinnest success path** (one user enrolls / one SkillSwap book+pay). Do not staff analytics (W12b) or fancy search (W5). Trace one booking: W1+W2 → W4 → W6 → W8. Fix those handoffs. End-to-end every day after.

Healthcare.gov is Module 2’s cost: no shared DAG, no critical path, integration last. We already put BLOCKED cancel on the booking chain so two refund systems cannot hide in separate contractor plans.
