# T1: Seed Postgres with 3 providers, services, and hardcoded slots

**AI-ready:** Yes  
**Slice:** 1 — Browse and Book (Seeded Provider)

## 1. Title
Seed Postgres with 3 providers, services, and hardcoded slots

## 2. Context (Why)
Slice 1 needs deterministic marketplace data so a learner can browse and book without provider onboarding. Seed data unblocks T2–T4 demos.

## 3. Scope (What)
- Add SQL migration or idempotent seed script that inserts exactly 3 providers, each with 1 service and 3 future slots.
- Script is runnable via `npm run db:seed` or `python -m app.scripts.seed_slice1` (match existing repo package manager; prefer one existing pattern).
- Re-running seed does not duplicate rows (upsert on stable seed IDs).

## 4. Interface Contract (Inputs/Outputs/Data Shapes)

### Tables (create if missing)

`providers`
| column | type | notes |
|--------|------|-------|
| id | UUID PK | fixed seed UUIDs below |
| display_name | TEXT NOT NULL | |
| bio | TEXT | nullable |
| category | TEXT NOT NULL | e.g. `guitar`, `yoga`, `coding` |
| city | TEXT NOT NULL | default `Austin` |
| created_at | TIMESTAMPTZ NOT NULL | `now()` |

`services`
| column | type | notes |
|--------|------|-------|
| id | UUID PK | fixed seed UUIDs |
| provider_id | UUID FK → providers.id | |
| title | TEXT NOT NULL | |
| description | TEXT | |
| duration_minutes | INT NOT NULL | 60 |
| price_cents | INT NOT NULL | integer cents |
| created_at | TIMESTAMPTZ NOT NULL | |

`slots`
| column | type | notes |
|--------|------|-------|
| id | UUID PK | fixed seed UUIDs |
| service_id | UUID FK → services.id | |
| starts_at | TIMESTAMPTZ NOT NULL | UTC |
| ends_at | TIMESTAMPTZ NOT NULL | starts_at + duration |
| status | TEXT NOT NULL | `open` \| `booked` ; seed all `open` |

### Fixed seed IDs
```
provider-1: 11111111-1111-4111-8111-111111111111
provider-2: 22222222-2222-4222-8222-222222222222
provider-3: 33333333-3333-4333-8333-333333333333
service-1:  a1111111-1111-4111-8111-111111111111  → provider-1
service-2:  a2222222-2222-4222-8222-222222222222  → provider-2
service-3:  a3333333-3333-4333-8333-333333333333  → provider-3
slot-1a:    b1111111-1111-4111-8111-111111111101  → service-1
slot-1b:    b1111111-1111-4111-8111-111111111102
slot-1c:    b1111111-1111-4111-8111-111111111103
slot-2a..c: b2222222-2222-4222-8222-222222222201..203
slot-3a..c: b3333333-3333-4333-8333-333333333301..303
```

Slot times: next Monday/Tue/Wed at 15:00 UTC relative to seed run day (document formula in script comments).

### Exit codes
- `0` on success; print `{"seeded":true,"providers":3,"services":3,"slots":9}`
- Non-zero if `DATABASE_URL` missing or migration fails

## 5. Acceptance Criteria

1. **Given** `DATABASE_URL` points at an empty SkillSwap Postgres DB  
   **When** the seed command runs  
   **Then** exit code is 0 and stdout JSON includes `"providers":3,"services":3,"slots":9`

2. **Given** seed already ran once  
   **When** seed runs again  
   **Then** row counts remain 3/3/9 (no duplicates) and exit code is 0

3. **Given** seed completed  
   **When** `SELECT count(*) FROM providers`  
   **Then** result is `3`

## 6. Constraints
- Stack: PostgreSQL 15+, same connection pattern as existing app (`DATABASE_URL`).
- No SQLite.
- UUIDs must match the fixed list above (frontend/demo scripts may hardcode them).
- Do not invent Redis/auth for this ticket.

## 7. Anti-Scope
- No HTTP endpoints
- No UI
- No payments, email, search, ratings
- No real provider registration
- No double-booking logic
