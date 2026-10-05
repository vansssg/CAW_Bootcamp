# Module 06 — Interface Contracts

Source tickets: Module 05 T2, T3, T5. Standards: `artifacts/standards/api-cross-cutting.md`.

## Shared types (all streams)

| Name | Type | Rules |
|------|------|-------|
| `provider_id` | UUID v4 | Fixed seeds from T1 |
| `service_id` | UUID v4 | |
| `slot_id` | UUID v4 | |
| `user_id` / `learner_id` | UUID v4 | Auth uses `user.id`; booking later uses `learner_id` — **same UUID space** |
| `datetime` | string | ISO-8601 UTC with `Z` suffix, e.g. `2026-09-01T15:00:00Z` |
| `date` | string | `YYYY-MM-DD` (UTC calendar date) |
| `slot_status` | enum | **`open` \| `booked` only** — never `available` / `free` |
| `error` | object | `{ "error": { "code": string, "message": string } }` |

Seed provider-1: `11111111-1111-4111-8111-111111111111`

---

## CONTRACT C1: Marketplace list (T2) ↔ Slots (T3)

**Pair:** Stream S1 ↔ Stream S2  
**Sync:** Both consume T1 seed; T3 path param `provider_id` MUST equal a `providers[].id` from T2.

### S1 provides — `GET /api/providers`
**Auth:** none  
**200:**
```json
{
  "providers": [
    {
      "id": "11111111-1111-4111-8111-111111111111",
      "display_name": "string",
      "category": "string",
      "city": "string",
      "bio": "string|null",
      "service": {
        "id": "a1111111-1111-4111-8111-111111111111",
        "title": "string",
        "duration_minutes": 60,
        "price_cents": 5000
      }
    }
  ]
}
```
**500:** `{ "error": { "code": "internal_error", "message": "string" } }` (no stack traces)

### S2 provides — `GET /api/providers/{provider_id}/slots`
**Auth:** none  
**Path:** `provider_id` UUID required  
**200:**
```json
{
  "provider_id": "11111111-1111-4111-8111-111111111111",
  "slots": [
    {
      "id": "b1111111-1111-4111-8111-111111111101",
      "service_id": "a1111111-1111-4111-8111-111111111111",
      "starts_at": "2026-09-01T15:00:00Z",
      "ends_at": "2026-09-01T16:00:00Z",
      "status": "open",
      "price_cents": 5000
    }
  ]
}
```
**400:** `invalid_provider_id`  
**404:** `provider_not_found`  
**500:** `internal_error`

### Assumptions
- S2 filters to `status == "open"` for booking consumers (booked rows omitted or included with status — **contract: omit booked** from default list).
- `price_cents` on slots matches parent service from T1/T2.

---

## CONTRACT C2: Auth register (T5) ↔ future Booking (T4/T6)

**Pair:** Stream S3 produces identity consumed later by booking.  
**Published now so S3 cannot invent integer user ids.**

### S3 provides — `POST /api/auth/register`
**Auth:** none (public)  
**Body required:** `email`, `password` (8–128), `display_name`, `role` ∈ {`learner`,`provider`,`both`}  
**Unknown keys:** 400 `invalid_body`  
**201:**
```json
{
  "user": {
    "id": "uuid",
    "email": "learner@example.com",
    "display_name": "Alex",
    "role": "learner",
    "provider_profile_id": null
  },
  "token": "string",
  "token_type": "Bearer",
  "expires_at": "2026-09-02T00:00:00Z"
}
```
**400:** `invalid_body`  
**409:** `email_taken`  
**429:** `rate_limited`  
**500:** `internal_error`

### Downstream consume rule (for T4/T6 agents)
- `Authorization: Bearer <token>`
- Booking `learner_id` **must** equal `user.id` (UUID string). Never invent parallel integer ids.

---

## CONTRACT C3: Error + ops (all streams)
Cite `artifacts/standards/api-cross-cutting.md`:
- 60 rpm writes → 429 `rate_limited`
- Unexpected → 500 `internal_error`, no stack traces
- Structured logs; never log raw passwords/tokens
