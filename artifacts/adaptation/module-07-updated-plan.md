# Module 07 — Updated Plan (6-day demo)

**Strategy:** Preserve and Patch + Minimal company bridge (DECIDE B)

## 1. Preserved
- T1 seed providers/services/slots (fixed UUIDs)
- T2 `GET /api/providers` contract C1 (shape unchanged)
- T3 `GET /api/providers/:id/slots` with `open`\|`booked` (Module 06 FIX)
- Module 06 isolated-branch process + CP1 enum gate
- `artifacts/standards/api-cross-cutting.md` citations

## 2. Modified
| Ticket | Change |
|--------|--------|
| T5 Register | Persist `company_name`, `can_book_for_others`; return on user object |
| T4 Create booking | Accept/validate/persist `booked_for_name`, `booked_for_email` when flag true; include in 201 |
| T6 My bookings | List includes `booked_for_*` if present |
| M06 contract C2 | Document bridge fields + flag gate |

## 3. Cut (safe because…)
| Item | Safe because |
|------|----------------|
| Slice 3 provider self-service | Seed covers browse/book |
| Live Stripe | Simulated pay OK for investor walkthrough |
| Advanced search/ratings | Demo path is known provider |
| Org RBAC / multi-admin | Meridian single booker + offline reimbursement |
| Email | UI confirmation shows booking id |
| Provider analytics | Not in Meridian path |

## 4. Added
| ID | Scope (one sentence) | Size |
|----|----------------------|------|
| T7 | Migration: add user `company_name`, `can_book_for_others`; booking `booked_for_name`, `booked_for_email` nullable | S |
| T8 | Patch register + seed one Meridian demo user (`can_book_for_others=true`, company_name=`Meridian Corp`) | S |
| T9 | Patch POST /api/bookings validation + response for delegate fields; Given/When/Then ACs | M |
| T10 | Minimal UI: show delegate fields when flag true; confirmation displays who booking is for | M |
| T11 | Debt ticket (post-demo): replace bridge with Organization entity + true delegation + org billing | L |

## Day plan (sketch)
- D1–2: T7+T8+finish T2/T3 merge  
- D3–4: T9 booking bridge + T4 race/409 still green  
- D5: T10 UI + T6 if time  
- D6: rehearse Meridian script; freeze cuts

---

## BREAK delta (RBAC — living update)

### Modified further
| Ticket | Additional change |
|--------|-------------------|
| T5/T7/T8 | Replace boolean with `org_role` + `department_id`; seed manager/employee/dept_head |
| T4/T9 | Authz: only `manager` (and dept_head if we allow) may set `booked_for_*`; employees 403 on book-for |
| T6 | **Promoted MUST:** filter list by role (own / dept / — managers may list who they booked) |

### Added
| ID | Scope | Size |
|----|-------|------|
| T12 | `require_role` dependency + matrix tests (employee/manager/dept_head) | M |

### Cut further to fund T12+T6
- T10 rich UI → API+minimal form only (or curl script for investor if UI slips)
- Any non-Meridian listing polish

### Preserved still
- T1–T3, slots enum `open`\|`booked`, no org billing, simulated pay OK
