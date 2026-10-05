# Production Module 08 DECIDE

## Decision 1 — deploy_strategy = blue_green (B)

This service just renamed `/ready` → `/readyz`. A rolling cut would serve **both** probe paths at once: old instances 404-or-503 on `/ready`, new instances 404 on `/ready` and 503/200 on `/readyz`. An LB still pointed at `/ready` would mark green instances dead while blue still looks “the old healthy.” Schema is additive (`CREATE TABLE IF NOT EXISTS analytics`), so mixed versions can share Postgres — the incompatibility is the **health path**, not the table.

Tradeoff: blue-green wants 2× CPU/RAM during the cut. This workspace is one laptop, Docker Desktop down, no Railway. Accept 2× only as “start a second process, smoke it, then switch,” not as a cloud replica set. Rollback is “point traffic back at the still-running blue,” which matches Knight (keep the old servers until green is proven).

Rejected rolling: zero-downtime is fake here anyway — we have one named container `url-shortener-prod`. Replacing it is already a stop/start gap. Rolling’s mixed-version window is the actual risk.

## Decision 2 — rollback_approach = automated (A)

`/live` `{ok:true}` is the CONTEXT incident (23 min of 500s). Automated rollback on `/live` would never fire. Automated rollback on **`/readyz` 503 N times plus a failed smoke `POST /links`** is the signal we actually measured.

Tradeoff: a Postgres blip during deploy rolls back a good image. That is cheaper than 3 AM “probably look at the dashboard” — there is no scraper here. Manual rollback assumes a human watching; Friday 5 PM walk-away is how Knight ran 45 minutes.

Rejected purely-manual: this laptop has no pager. A one-command revert (`git revert --no-edit HEAD`) still exists as the human override after an automated bounce.
