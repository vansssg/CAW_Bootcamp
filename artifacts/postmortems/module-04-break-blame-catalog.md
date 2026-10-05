# Module 04 BREAK — blame catalog (same incident, bad postmortem)

## Blame / individual-targeting instances (≥15)

1. “John Chen deployed…” (summary — names deployer as causal actor)  
2. “which contained a breaking configuration change” tied to John in same breath  
3. “John removed the warehouse_routing config field without verifying…”  
4. “This should not have happened.” (judgmental)  
5. “John pushed the v2.14 release…”  
6. “John did not check whether the production service still read it”  
7. “This was an oversight on John's part.”  
8. “Maria Santos… initially dismissed”  
9. “Maria should have investigated immediately”  
10. “Maria could have checked the database directly sooner”  
11. “Maria identified… attempted a rollback” (context of prior blame)  
12. “DevOps had not updated it” / implied fault on DevOps  
13. “Kevin Park… eventually did the manual rollback” (hero/villain framing vs system)  
14. Root cause: “John removed a config field…”  
15. “The change was not properly tested” + “John should have verified…”  
16. CF: “Maria did not investigate… quickly enough”  
17. CF: “Kevin's team had not maintained the rollback automation”  
18. CF: “John did not do a thorough enough review…”  
19. AI1: “John will be more careful…”  
20. AI2: “Remind the team to always check…” (try harder)  
21. AI3: “Maria should set up better monitoring…”  
22. AI4: “Kevin's team should fix…” (named via Kevin)  
23. Lessons: “if John had done more thorough testing”  
24. Lessons: “everyone should double-check their work”  

**Count: 24**

## Answers

1. **Missed systemic root cause:** Silent success path (try/except → 200), HTTP-only monitoring, staging≠prod config, no payment/order reconciliation—not “John removed a field.”  
2. **System changes among 5 AIs:** At most **1–2** (rollback fix; maybe monitoring if rewritten). Items 1–2–3–5 are “be more careful” / remind / individual.  
3. **Near-miss reporting:** John/Maria/Kevin would **hide** near-misses—names circulated as fault.  
4. **What it prevents:** Almost nothing for the *next* engineer. No invariant tests, alerts, or fail-closed behavior.
