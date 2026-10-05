# Module 05 BREAK Response

## New failure state
- Auth bypass is patched, but post-incident audit indicates completed data loss:
  - 12 deleted links
  - 8 affected user accounts
  - source IP 203.0.113.42

## Immediate response plan (post-breach, post-fix)
1. Preserve evidence:
   - freeze relevant access logs and admin-route request logs for incident window.
   - snapshot current DB state before any restoration attempts.
2. Scope blast radius:
   - identify exact deleted records and account ownership.
   - map deletion timeline and compare against exploit timeline.
3. Recovery strategy:
   - restore deleted rows from DB backup/PITR if available.
   - if no direct row-level restore path, reconstruct from secondary data sources (analytics rows, user exports, audit trails).
4. Stakeholder communication:
   - send explicit impact notice to internal stakeholders with affected-count metrics.
   - avoid speculative recovery ETA until backup viability is validated.
5. Customer handling:
   - prepare affected-user notification draft once record list is confirmed.
6. Follow-up controls:
   - add mandatory admin-delete audit logging and alerting thresholds.
   - rotate admin auth secret and invalidate stale credentials/tokens.

## Command/verification limitation
- Live DB validation commands for deleted-row recovery could not be executed in this environment because local DB connectivity remained unavailable.
- Limitation is explicitly recorded; no recovery success was fabricated.
