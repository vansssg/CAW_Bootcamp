# Module 06 — Parallel Execution Plan

**Mode:** `standalone_simulated`  
**Parallelism strategy:** `isolated_branches` (DECIDE B)  
**Sync point design:** `checkpoint_syncs` (Decision 2 — applied; CLI advanced after D1)

## Constraints twist (from Module 05)
- Prescriptive tickets + cite `artifacts/standards/api-cross-cutting.md`
- IDs are UUID; slot status enum includes `open` | `booked` (not `available`)
- Error envelope: `{ "error": { "code", "message" } }`

## Selected parallel streams

| Stream | Ticket | Branch | Depends on | Why parallel-safe |
|--------|--------|--------|------------|-------------------|
| S1 | T2 GET `/api/providers` | `agent/t2-providers` | T1 seed only | No hard dep on T3/T5 |
| S2 | T3 GET `/api/providers/:id/slots` | `agent/t3-slots` | T1 seed only | No hard dep on T2/T5 |
| S3 | T5 POST `/api/auth/register` | `agent/t5-auth` | none (own tables) | No hard dep on T2/T3 |

**Not parallelized:** T4 (needs T3 slot contract + seed); T6 (needs T4+T5).

## Coordinator workflow
1. Confirm T1 seed UUIDs frozen (Module 05 T1).
2. Publish contracts → `artifacts/contracts/module-06-interface-contracts.md`.
3. Launch S1/S2/S3 on isolated branches (simulated below).
4. **Checkpoint CP1** after first meaningful output (handler + response schema stub).
5. Agents finish → merge S1, then S2, then S3 → **Checkpoint CP2** integration smoke.
6. Detect/fix seeded contract violation before claiming done.

## Checkpoints

### CP1 — Schema freeze (after ~30% of each stream)
Verify each stream’s OpenAPI/JSON example matches the contract doc:
- S1: `providers[].id` UUID + nested `service`
- S2: `slots[].status` ∈ {`open`,`booked`}; times ISO-8601 `Z`
- S3: `token` + `user.id` UUID; `provider_profile_id` null|UUID

### CP2 — Integration smoke (post-merge)
- Seed present → `GET /api/providers` returns 3
- Pick provider-1 → slots ≥ 3 with `status:"open"`
- Register learner → 201 + token
- Cross-check: no stream introduced `available` or integer ids

## Rollback
If a stream violates contract at CP1: discard that branch, re-prompt agent with contract excerpt, keep other branches.
