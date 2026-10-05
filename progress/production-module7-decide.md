# Production Module 07 DECIDE — runbook format

Choice: **A linear checklist** (`decisions.module_07.runbook_format = checklist`)

## Audience

Not only the person who built the URL shortener. First on-call who has never opened `api/app/main.py`. Also 3 AM me, legally-drunk-tired.

## Why A

Wrong branch is more dangerous than 5 wasted minutes. CONTEXT: sleep dep hits decision-making hardest. A tree that asks “error rate >5% but <10% and p95 <2s?” is how you `docker rm` instead of `docker restart`. A numbered list with **exact commands** (`docker restart myservice-prod`, never “restart the service”) is the five-character lesson.

This workspace already has three M04 checklists (high error, high latency, service down). Operator M07 should stay that shape so a pager can copy-paste.

## Tradeoff accepted

We will walk “check /live” even when the page already says Postgres. Cost: a couple of timed curls. Benefit: cannot skip the step that distinguishes process-dead vs breaker-open (~4s `/ready` vs dead `/live`).

## Rejected B for stored format

Trees map to debugging at 2 PM. At 3 AM they are extra cognition. Hybrid in practice: one **three-line symptom index** at the top that points at three **linear** checklists — routing is not a nested tree; the stored format is still checklist.
