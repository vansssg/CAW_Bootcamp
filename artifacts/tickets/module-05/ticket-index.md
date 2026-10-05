# Module 05 — Ticket Index (SkillSwap)

**Source slices:** `artifacts/slices-module-04.md`  
- Slice 1: Browse and Book (Seeded Provider)  
- Slice 2: User & Provider Identity Ownership  

**Decisions applied**
- `ticket_format` = **prescriptive** (DECIDE A)
- `acceptance_criteria_style` = **given_when_then** (applied in all tickets; CLI advanced after Decision 1)

**Standards (BREAK/FIX)**
- All tickets cite `artifacts/standards/api-cross-cutting.md`
- T4 named exception: `SLICE1_GUEST_LEARNER` (revoked by T6)

| ID | Title | Slice | AI-ready | Est. |
|----|-------|-------|----------|------|
| T1 | Seed Postgres with 3 providers, services, and hardcoded slots | 1 | Yes | 1h |
| T2 | GET /api/providers — list seeded providers | 1 | Yes | 1.5h |
| T3 | GET /api/providers/:id/slots — list hardcoded available slots | 1 | Yes | 1.5h |
| T4 | POST /api/bookings — create booking (guest learner_id) | 1 | Yes | 2h |
| T5 | POST /api/auth/register + provider profile row | 2 | Yes | 2h |
| T6 | GET /api/bookings/me — list own bookings (ownership check) | 2 | Yes | 1.5h |

**Dependency order:** T1 → T2 → T3 → T4 → T5 → T6  
T2/T3 can run in parallel after T1. T5 after T4. T6 after T5.

**Files**
- `t1-seed-providers.md`
- `t2-get-providers.md`
- `t3-get-provider-slots.md`
- `t4-post-bookings.md`
- `t5-auth-register-provider.md`
- `t6-get-my-bookings.md`
