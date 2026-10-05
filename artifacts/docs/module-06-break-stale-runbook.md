# Module 06 BREAK — three 3 AM failures in the “clean” runbook

Compared to OrderFlow BUILD description (`DATABASE_URL`, worker, `helm rollback`).

## Failure 1 — “Rollback” that is not a rollback (most dangerous)
Step 6 says:
`helm upgrade orderflow deploy/charts/orderflow --namespace production --set image.tag=latest`

That **redeploys `latest`**, often the **same broken image**, and is not `helm rollback`. At 3 AM this **extends** the outage or re-breaks a partial recovery.

## Failure 2 — Stale / wrong secret name
Uses `DB_CONNECTION_STRING` / `printenv DB_CONNECTION_STRING`. Service truth is **`DATABASE_URL`**. On-call gets empty/wrong env → false “config missing” rabbit hole while Postgres may be fine.

## Failure 3 — Hidden tool / worker gaps that stall recovery
- Requires `jq` with no install/check (curl alone would work).  
- No Celery/worker path though refunds fail when worker is down (common OrderFlow failure mode).  
- `printenv` of DB URL dumps secrets into shell scrollback/incident notes.

Any one wastes minutes; #1 actively harms.
