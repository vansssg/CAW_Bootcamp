# Module 06 — Simulated agent output bundle

**Mode:** `standalone_simulated`  
**Branches:** `agent/t2-providers`, `agent/t3-slots`, `agent/t5-auth`  
**Note:** Payloads below are realistic agent deliveries for CP1/CP2 review — not live runtime output.

---

## Stream S1 — T2 GET /api/providers (`agent/t2-providers`)

### Files claimed
- `api/app/routers/providers.py` — `list_providers`
- `api/app/schemas/providers.py` — `ProviderListResponse`

### Sample response (CP1)
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "providers": [
    {
      "id": "11111111-1111-4111-8111-111111111111",
      "display_name": "Ava Strings",
      "category": "guitar",
      "city": "Austin",
      "bio": "Fingerstyle coach",
      "service": {
        "id": "a1111111-1111-4111-8111-111111111111",
        "title": "60-min guitar lesson",
        "duration_minutes": 60,
        "price_cents": 5000
      }
    },
    {
      "id": "22222222-2222-4222-8222-222222222222",
      "display_name": "Ben Flow",
      "category": "yoga",
      "city": "Austin",
      "bio": null,
      "service": {
        "id": "a2222222-2222-4222-8222-222222222222",
        "title": "Yoga fundamentals",
        "duration_minutes": 60,
        "price_cents": 4000
      }
    },
    {
      "id": "33333333-3333-4333-8333-333333333333",
      "display_name": "Cara Code",
      "category": "coding",
      "city": "Austin",
      "bio": "Python tutoring",
      "service": {
        "id": "a3333333-3333-4333-8333-333333333333",
        "title": "Intro to Python",
        "duration_minutes": 60,
        "price_cents": 6000
      }
    }
  ]
}
```

### CP1 check
- [x] UUID ids  
- [x] Nested `service` shape matches C1  
- [x] Error envelope ready for 500  

---

## Stream S2 — T3 GET /api/providers/:id/slots (`agent/t3-slots`)

### Files claimed
- `api/app/routers/providers.py` — `list_provider_slots` (same router file; isolated branch)

### Sample response (CP1) — **SEEDED CONTRACT VIOLATION**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "provider_id": "11111111-1111-4111-8111-111111111111",
  "slots": [
    {
      "id": "b1111111-1111-4111-8111-111111111101",
      "service_id": "a1111111-1111-4111-8111-111111111111",
      "starts_at": "2026-09-01T15:00:00Z",
      "ends_at": "2026-09-01T16:00:00Z",
      "status": "available",
      "price_cents": 5000
    },
    {
      "id": "b1111111-1111-4111-8111-111111111102",
      "service_id": "a1111111-1111-4111-8111-111111111111",
      "starts_at": "2026-09-02T15:00:00Z",
      "ends_at": "2026-09-02T16:00:00Z",
      "status": "available",
      "price_cents": 5000
    }
  ]
}
```

### Violation detail
| Field | Contract (C1) | Agent S2 output | Impact |
|-------|---------------|-----------------|--------|
| `slots[].status` | enum `open` \| `booked` | `"available"` | Booking consumer (T4) filters `status=="open"` → **empty slots / false 409s** |

### CP1 result
- [x] UUID + ISO-8601 OK  
- [ ] **FAIL** status enum — must remap `available` → `open` before merge  

### Corrected payload (post-fix, for CP2)
```json
{ "status": "open" }
```
on each open slot; booked rows omitted per C1.

---

## Stream S3 — T5 POST /api/auth/register (`agent/t5-auth`)

### Sample response (CP1)
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "user": {
    "id": "c0000000-0000-4000-8000-0000000000aa",
    "email": "learner@example.com",
    "display_name": "Alex",
    "role": "learner",
    "provider_profile_id": null
  },
  "token": "simulated_token_urlsafe_32chars_xxxxxx",
  "token_type": "Bearer",
  "expires_at": "2026-09-02T00:00:00Z"
}
```

### CP1 check
- [x] `user.id` UUID (not integer — avoids Mars-Orbiter-style ID drift)  
- [x] `token_type` Bearer  
- [x] 409 `email_taken` documented in router comments  

---

## CP2 integration notes
1. Merge S1 first (clean).  
2. Block S2 merge until status enum fixed.  
3. Merge S3.  
4. Smoke: providers → slots(`open`) → register.  

**Lesson:** Isolated branches + checkpoint sync caught the enum drift at CP1 instead of at booking integration day.
