# Module 06 FIX — corrected Step 6 + env + tools

## Immediate corrections to the broken runbook
1. Replace Step 6 deploy “fix” with:
```bash
helm history orderflow --namespace production
helm rollback orderflow --namespace production
kubectl -n production rollout status deploy/orderflow-api
```
Never `image.tag=latest` as rollback.
2. Replace every `DB_CONNECTION_STRING` with `DATABASE_URL` (match app). Prefer `psql "$DATABASE_URL" -c 'SELECT 1'` over printing secrets.
3. Drop hard `jq` dependency (`curl -sS URL`); add worker section (queue depth + restart `orderflow-worker`).

## Prevention
- Quarterly runbook drill in staging  
- CI link/command smoke where possible  
- One canonical env table at top (our runbook already)

Our `module-06-orderflow-runbook.md` already uses `helm rollback` + `DATABASE_URL` + worker §3.
