# T6: GET /api/bookings/me — list own bookings with ownership check

**AI-ready:** Yes  
**Slice:** 2 — User & Provider Identity Ownership  
**Depends on:** T4, T5

## 1. Title
GET /api/bookings/me — list bookings for the authenticated user

## 2. Context (Why)
Learners must see only their bookings. Slice 2 acceptance requires ownership enforcement so users cannot read another user's bookings.

## 3. Scope (What)
- Add auth dependency that resolves `Authorization: Bearer` → `users.id`.
- Update `POST /api/bookings` to require auth and set `learner_id` from the token user (ignore/forbid body `learner_id`).
- Implement `GET /api/bookings/me` filtered by `learner_id = current_user.id`.
- Implement negative path: `GET /api/bookings/{id}` returns 404 (not 403) if booking belongs to another user.

## 4. Interface Contract

### Auth
Header required: `Authorization: Bearer <token>`  
Missing/invalid → `401` `{ "error": { "code": "unauthorized", "message": "..." } }`

### GET /api/bookings/me — `200`
```json
{
  "bookings": [
    {
      "id": "uuid",
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
  ]
}
```

### GET /api/bookings/{booking_id}
- Owner → `200` with single `booking` object (same fields as list item)
- Other user / missing → `404` `{ "error": { "code": "booking_not_found", "message": "Booking not found" } }`

### POST /api/bookings (updated)
Request body becomes:
```json
{ "slot_id": "uuid" }
```
`learner_id` taken from auth context only.

### Function signatures
```python
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth import require_user  # resolve Bearer token → User

@router.get("/bookings/me")
def get_my_bookings(user: User = Depends(require_user), db: Session = Depends(get_db)) -> BookingListResponse: ...

@router.get("/bookings/{booking_id}")
def get_booking(booking_id: UUID, user: User = Depends(require_user), db: Session = Depends(get_db)) -> BookingResponse: ...
```
Sync SQLAlchemy only.

## 5. Acceptance Criteria

1. **Given** user A with a confirmed booking  
   **When** `GET /api/bookings/me` with A's token  
   **Then** 200 and the list includes that booking id

2. **Given** user A owns booking X; user B is authenticated  
   **When** B calls `GET /api/bookings/{X}`  
   **Then** 404 with `error.code == "booking_not_found"` (no data leak)

3. **Given** no Authorization header  
   **When** `GET /api/bookings/me`  
   **Then** 401 with `error.code == "unauthorized"`

4. **Given** authenticated user  
   **When** `POST /api/bookings` with only `slot_id` for an open slot  
   **Then** 201 and `booking.learner_id` equals the authenticated user id

5. **Given** provider profile from T5 (`role` provider/both)  
   **When** `SELECT id FROM provider_profiles WHERE user_id = :user`  
   **Then** exactly one row exists (identity ready for Slice 3)

## 6. Constraints
- Never return another user's booking fields on 403/404 paths.
- Keep error envelope consistent with T2–T5.
- Guest `learner_id` in body must be rejected with 400 `invalid_body` after this ticket — **revokes** `SLICE1_GUEST_LEARNER` from T4.
- Cite `artifacts/standards/api-cross-cutting.md`: Bearer required on mutating + `/bookings/me`; rate limits; safe 500s; log `event=bookings_listed` / `booking_created` without tokens.
- **Authz:** list/get only rows where `learner_id == current_user.id`. Providers use a different future endpoint (anti-scope).
- **Integration:** T4 seed UUIDs and booking JSON field names are the contract; do not rename `starts_at`/`provider_display_name`.
- **Unexpected errors:** 500 `internal_error` only; never stack traces.

## 7. Anti-Scope
- No provider dashboard / provider-facing booking list
- No cancellation
- No admin override
- No pagination
- No social login
