# Module 2 CONTEXT — writing that can be scanned under fire

Knight Capital (Aug 2012): a deploy reactivated dead trading code. The rollback lived in a runbook that was a wall of paragraphs — no headings, no bullets. ~$440M in 45 minutes. The information existed; the writing was not scannable.

A runbook is the emergency instruction sheet: which lever, in which order, while the building is on fire. LEGO-instruction bar: step-by-step, unambiguous, not fancy.

## Micro-exercise (real artifact)

Document: `progress/technical-communication/code-review.md` from Module 1.

1. Main point without opening: request changes — `total_age / cnt` ZeroDivisionError and mixed-average must be fixed; names/dataclass are not blockers.
2. Find in 10 seconds: yes — `## Required Changes (Bugs)` then **1. [blocker]**.
3. Headings-only skim: Decision, Strengths, Required Changes, Suggestions, Final Verdict — a reader knows the map.

Contrast that with the Knight runbook (no headings). Module 1 already used severity headings; Module 2 is the same skill for prose you write from scratch.

Risk named: buried lede. Mitigation: heading + first sentence = the action.
