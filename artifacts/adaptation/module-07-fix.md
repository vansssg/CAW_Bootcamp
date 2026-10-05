# Module 07 FIX — stabilize after double change

## Locked decisions
1. **Thin roles** (`employee`|`manager`|`dept_head` + `department_id`) for Meridian demo — not full Organization billing.
2. **Preserve** T1–T3 and Module 06 contracts; **patch** auth/booking.
3. **MUST:** T1–T5, T6 list authz, T7–T9, T12 role middleware.
4. **CUT:** org invoice, provider self-service, live Stripe, email, T10 polish.

## Permission matrix (demo)
| Role | POST book for other | GET own bookings | GET dept bookings |
|------|---------------------|------------------|-------------------|
| employee | no (403) | yes | no |
| manager | yes | yes | no (unless also head) |
| dept_head | no* | yes | yes (same department_id) |

\*dept_head view-only unless also flagged manager in seed — keep simple: heads view dept, managers book-for.

## Acceptance smoke
1. Manager books for employee email → 201 with booked_for_*  
2. Employee tries book-for → 403  
3. Employee GET me → only own  
4. Dept_head GET dept → only their department_id  

## PM note
v2 in `module-07-adaptation-note.md` is the sendable version.
