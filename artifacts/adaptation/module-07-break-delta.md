# Module 07 BREAK — second change (RBAC) layered on living docs

**Do not restart.** Updates below are deltas on STEP 3 artifacts.

## Decision B status
Original `can_book_for_others` boolean **no longer sufficient** (cannot express manager vs employee vs dept head).  
**Revised judgment:** keep bridge *spirit* (no full Organization billing) but **escalate identity to thin roles**:
- `org_role`: `employee` | `manager` | `dept_head`
- `department_id` UUID nullable (seeded depts for Meridian demo only)
- Permissions in middleware; still **no** company invoicing / multi-org admin console in 6 days

This is a **partial retract of pure Option B**, not a flip to full Option A.

## 1. NEW / escalated impacts
| Artifact | Was | Now | Why |
|----------|-----|-----|-----|
| Auth/JWT | MINOR | **MAJOR** | Role + department claims in session/token; every booking route checks role |
| User data model | MINOR | **MAJOR** | roles + department_id (boolean flag demoted/removed) |
| Booking GET list | SHOULD | **MUST** (T6) | Employees view-own; managers book-for; dept_head list-by-dept — needs list endpoint |
| Provider dashboard | NO IMPACT | MINOR | Optional display of booker role — skip if cut |

## 2. MINOR → MAJOR
- User model, Auth, Booking API authorization checks, contracts C2/C3 authz section

## 3. CUT list changes
| Change | Action |
|--------|--------|
| T6 my-bookings | **CUT → MUST SHIP** (RBAC visibility) |
| T10 fancy UI | **SHOULD → CUT** if behind; prefer API+thin form |
| Simulated payment | stays CUT/sim |
| Org invoicing | stays CUT |
| **NEW CUT:** T10 polish / animations / non-Meridian listing tweaks | make room for authz |
| Provider self-service | stays CUT |

## 4. Impact statement — revised
See updated `module-07-adaptation-note.md` (RBAC paragraph added; day-6 honesty).

## 5. Plan delta
See `module-07-updated-plan.md` section **BREAK delta**.
