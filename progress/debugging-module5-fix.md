# Module 05 FIX (Data Loss After Exploit)

## Backup/PITR assessment
- Available per scenario constraints:
  - full backup at 06:00 UTC
  - continuous WAL/binlog archiving
  - point-in-time recovery available
  - deleted rows existed before attack window
- Conclusion: targeted row restoration is feasible without full-database rollback.

## Recovery execution plan
1. Create a temporary recovery clone at timestamp **2024-03-15 14:20:00 UTC**.
2. Query recovery clone for the 12 deleted link records tied to exploit window.
3. Export required rows with canonical fields used by production `links` table.
4. Reinsert missing rows into primary database in a controlled transaction.
5. Validate restored links through lookup/redirect checks and count reconciliation.
6. Capture incident audit record listing restored IDs, operator, and timestamp.

## Safety controls during restore
- Freeze admin delete operations until restore verification completes.
- Snapshot current production state before any reinsert.
- Reinsert only missing IDs/codes (idempotent restore logic) to avoid overwrites.

## Stakeholder data-loss communication (final)
Follow-up on the security incident: during the attack window, 12 short links belonging to 8 users were deleted before the auth bypass was patched. Recovery is being executed using point-in-time database reconstruction from before the exploit window. We will confirm restoration counts and functional link checks immediately after validation, then notify affected users with a clear impact summary.

## Evidence/limitation note
- This environment could not execute live PITR or production restore commands due local database connectivity constraints.
- Therefore, this FIX records a concrete and auditable recovery plan and communication output without fabricating restore completion.
