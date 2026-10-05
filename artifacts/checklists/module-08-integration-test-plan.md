# Module 08 — Integration test plan

**Verification strategy applied:** combined (scenarios first, then requirements walkthrough in traceability matrix).

## Scenario 1 — Happy path booking (Meridian manager)
| Step | Component | Expected | Actual (sim) |
|------|-----------|----------|--------------|
| 1 List providers | T2 | 200, 3 providers UUID | PASS |
| 2 View slots | T3 | status open, ISO times | PASS |
| 3 Register/login manager | T5 | token + org_role=manager | PASS |
| 4 POST booking w/ booked_for | T4 | 201 confirmed + booked_for_* | PASS |
| 5 GET my/dept lists | T6 | manager sees booking | PASS |
| 6 Provider dashboard | — | CUT — skip | N/A |
| 7 Email confirm | — | CUT — UI shows id | N/A |

## Scenario 2 — Cancellation
| Step | Expected | Actual |
|------|----------|--------|
| Cancel booking + refund policy | U-F7/U-F8 | **DEFERRED** — Module 07 CUT; blocked until PM cancel policy (U-F8) |
| Status propagation | — | Not built — mark LOST/deferred in matrix |

## Scenario 3 — Concurrent booking
| Step | Expected | Actual (sim) |
|------|----------|--------------|
| Two POST same slot_id | one 201, one 409 `slot_unavailable` | PASS (unique + conditional update) |
| No double row | count=1 | PASS |

## Scenario 4 — RBAC employee
| Step | Expected | Actual |
|------|----------|--------|
| Employee POST booked_for | 403 | PASS |
| Employee GET me | own only | PASS |
| Dept_head GET dept | same department_id only | PASS |

## Scenario 5 — Edge: closed slot
| Step | Expected | Actual |
|------|----------|--------|
| Book status booked slot | 409 | PASS |
