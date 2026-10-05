# T4: POST /api/bookings — create a booking (guest learner_id)

**AI-ready:** Yes  
**Slice:** 1 — Browse and Book (Seeded Provider)  
**Depends on:** T1, T3

## 1. Title
POST /api/bookings — create a new booking

## 2. Context (Why)
Completes the Slice 1 happy path: learner submits a booking for an open seeded slot and receives a durable confirmation id. Auth arrives in Slice 2; this ticket accepts an explicit `learner_id` UUID in the body (guest placeholder).

## 3. Scope (What)
- Create `bookings` table + `POST /api/bookings`.
- On success: insert booking, set slot `status='booked'`.
- Persist in Postgres (survives process restart).
- File: `api/app/routers/bookings.py`, schema in `api/app/schemas/bookings.py`.

## 4. Interface Contract

### Table `bookings`
| column | type | notes |
|--------|------|-------|
| id | UUID PK | gen_random_uuid() |
| learner_id | UUID NOT NULL | from request body (guest) |
| provider_id | UUID NOT NULL | denormalized from slot/service |
| service_id | UUID NOT NULL | |
| slot_id | UUID NOT NULL UNIQUE | one booking per slot |
| status | TEXT NOT NULL | `confirmed` |
| created_at | TIMESTAMPTZ NOT NULL | |

### Request
```http
POST /api/bookings
Content-Type: application/json
Idempotency-Key: <optional uuid string>

{
  "learner_id": "c0000000-0000-4000-8000-000000000001",
  "slot_id": "b1111111-1111-4111-8111-111111111101"
}
```

**Required fields:** `learner_id` (UUID), `slot_id` (UUID).  
**Optional headers:** `Idempotency-Key` (string, 8–128 chars).  
**Forbidden:** any other body keys (e.g. `notes`, `provider_id`, `status`) → `400` `invalid_body`. No free-text/HTML fields in Slice 1.

### Idempotency
- If `Idempotency-Key` is present and a prior successful booking was stored for the same key, return **200** with the original booking JSON (do not create a second row).
- Store keys in table `idempotency_keys(key TEXT PK, booking_id UUID NOT NULL, created_at TIMESTAMPTZ)`.
- If the same `learner_id` + `slot_id` is retried **without** a key and the slot is already `booked` by that learner, return **200** with that booking (safe retry). If booked by a **different** learner → **409** `slot_unavailable`.

### Response `201` (new booking)
```json
{
  "booking": {
    "id": "uuid",
    "learner_id": "uuid",
    "provider_id": "uuid",
    "service_id": "uuid",
    "slot_id": "uuid",
    "status": "confirmed",
    "provider_display_name": "string",
    "service_title": "string",
    "starts_at": "2026-09-01T15:00:00Z",
    "ends_at": "2026-09-01T16:00:00Z",
    "created_at": "2026-08-26T10:00:00Z"
  }
}
```

### Response `200` (idempotent replay)
Same JSON shape as `201`.

Error body: `{ "error": { "code": "string", "message": "string" } }`

### Errors
| status | code | when |
|--------|------|------|
| 400 | `invalid_body` | missing/invalid UUIDs, unknown fields, bad Idempotency-Key |
| 404 | `slot_not_found` | unknown slot_id |
| 409 | `slot_unavailable` | slot status ≠ `open` OR unique violation by another learner |
| 429 | `rate_limited` | per `artifacts/standards/api-cross-cutting.md` |
| 500 | `internal_error` | unexpected; **no stack traces** |

### DB session (match existing `api/app/db.py`)
This repo uses **sync** SQLAlchemy (`SessionLocal`), not async. If `get_db` is missing, add to `api/app/db.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Import: `from app.db import get_db`  
Handler uses `db: Session = Depends(get_db)` (sync `sqlalchemy.orm.Session`), not `AsyncSession`.

### Function signature
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter(tags=["bookings"])

@router.post("/bookings", status_code=201)
def create_booking(body: CreateBookingRequest, db: Session = Depends(get_db)) -> BookingCreateResponse: ...
```

Register in `api/app/main.py`: `app.include_router(bookings.router, prefix="/api")`.

### Resolve provider/service from slot (required join path)
```sql
SELECT s.id AS slot_id, s.status, s.starts_at, s.ends_at,
       svc.id AS service_id, svc.title AS service_title, svc.price_cents,
       p.id AS provider_id, p.display_name AS provider_display_name
FROM slots s
JOIN services svc ON svc.id = s.service_id
JOIN providers p ON p.id = svc.provider_id
WHERE s.id = :slot_id
```
Use this result to populate denormalized booking columns and the 201 response. Do not invent alternate join paths.

Transaction: read slot via join above → if `status != 'open'` return 409 → insert booking → `UPDATE slots SET status='booked' WHERE id=:slot_id AND status='open'` (0 rows ⇒ 409) → commit. On conflict rollback.

### VERIFY notes (AI roleplay — Module 05)
| # | Agent question | Classification | Resolution |
|---|----------------|----------------|------------|
| 1 | Where is `get_db`, and is the API async? | Spec gap | Sync `SessionLocal` + add `get_db` yield helper; import `from app.db import get_db` |
| 2 | How do I get `provider_display_name` / `service_title` from only `slot_id`? | Spec gap | Required JOIN path documented above |
| 3 | SQLAlchemy models vs raw SQL for the insert? | Implementation decision | Either OK if table/columns/statuses/response JSON match this contract |

## 5. Acceptance Criteria

1. **Given** an open seeded slot  
   **When** `POST /api/bookings` with valid `learner_id` + `slot_id`  
   **Then** 201 and body includes `booking.id`, `status:"confirmed"`, `provider_display_name`, `service_title`, `starts_at`

2. **Given** a successful booking  
   **When** process restarts and `SELECT * FROM bookings WHERE id = :id`  
   **Then** the row still exists (Postgres, not memory)

3. **Given** the same `slot_id` already booked by a **different** learner  
   **When** a second `POST /api/bookings` uses that slot  
   **Then** 409 with `error.code == "slot_unavailable"`

4. **Given** unknown `slot_id`  
   **When** POST  
   **Then** 404 with `error.code == "slot_not_found"`

5. **Given** a first successful POST with `Idempotency-Key: abc`  
   **When** the identical POST is retried with the same key  
   **Then** 200 and the same `booking.id` (no second row)

6. **Given** a body that includes an extra `notes` field  
   **When** POST  
   **Then** 400 with `error.code == "invalid_body"`

## 6. Constraints
- FastAPI + **sync** SQLAlchemy via existing `SessionLocal` / `get_db`; one DB transaction per request.
- Unique constraint on `bookings.slot_id` required.
- Confirmation payload must include provider name + service + time (Slice 1 AC).
- **Cite:** `artifacts/standards/api-cross-cutting.md` for rate limiting (60 rpm → 429), safe 500 envelope (no stack traces), and structured logging (`event=booking_created` with booking_id, learner_id, slot_id).
- **Named exception (BREAK fix):** Auth is deferred — public `POST /api/bookings` is allowed only under `SLICE1_GUEST_LEARNER`. Client may pass `learner_id` in the body. This exception is revoked by T6 (auth-bound learner_id). Comment in code: `SLICE1_GUEST_LEARNER`.
- **Authorization (FIX):** Any caller may book any open slot for the supplied `learner_id` while the guest exception is active (accepted Slice 1 risk). After T6, a user may book **only for themselves** (token user id == booking learner_id). Providers cannot create learner bookings via this endpoint.
- **Input (FIX):** Strict body allowlist (`learner_id`, `slot_id` only). No HTML/script-bearing fields in this ticket.
- **Idempotency (FIX):** Support `Idempotency-Key` + same-learner safe retry as specified above.

### FIX — three more unstated assumptions closed
1. Authorization / who can book for whom (guest vs self-only after T6)
2. Input allowlist / no free-text injection surface
3. Network-retry idempotency (`Idempotency-Key` + same-learner 200)

## 7. Anti-Scope
- No payment
- No email/SMS
- No cancellation
- No full auth middleware in this ticket (exception above; T5/T6 own identity)
- No double-booking beyond slot status + unique constraint + idempotency rules
- No UI page (API only; UI can be a later ticket)
- Do not re-implement global error middleware here — use/extend the shared handler per standards doc
- No `notes`/message fields
