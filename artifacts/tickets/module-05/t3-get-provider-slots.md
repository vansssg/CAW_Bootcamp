# T3: GET /api/providers/:id/slots — list hardcoded available slots

**AI-ready:** Yes  
**Slice:** 1 — Browse and Book (Seeded Provider)  
**Depends on:** T1

## 1. Title
GET /api/providers/:id/slots — get available time slots for a provider

## 2. Context (Why)
After choosing a provider, the learner picks an open slot. Slice 1 uses seeded/hardcoded open slots only (no calendar sync).

## 3. Scope (What)
- Implement `GET /api/providers/{provider_id}/slots`.
- Return only slots with `status = 'open'` for that provider's services.
- File: same providers router as T2.

## 4. Interface Contract

### Request
- Method: `GET`
- Path: `/api/providers/{provider_id}/slots`
- Path param: `provider_id` UUID

### Response `200`
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
`price_cents` comes from the parent service row.

### Response `404`
```json
{ "error": { "code": "provider_not_found", "message": "Provider not found" } }
```

### Response `400` (invalid UUID)
```json
{ "error": { "code": "invalid_provider_id", "message": "provider_id must be a UUID" } }
```

### Function signature
```python
from sqlalchemy.orm import Session
from app.db import get_db

@router.get("/providers/{provider_id}/slots")
def list_provider_slots(provider_id: UUID, db: Session = Depends(get_db)) -> ProviderSlotsResponse: ...
```

## 5. Acceptance Criteria

1. **Given** seeded provider-1  
   **When** `GET /api/providers/11111111-1111-4111-8111-111111111111/slots`  
   **Then** 200 and at least 3 slots with `status:"open"`

2. **Given** unknown UUID  
   **When** `GET /api/providers/99999999-9999-4999-8999-999999999999/slots`  
   **Then** 404 with `error.code == "provider_not_found"`

3. **Given** a slot row updated to `status='booked'`  
   **When** slots endpoint is called for that provider  
   **Then** that slot id is absent from `slots`

## 6. Constraints
- ISO-8601 UTC timestamps with `Z` suffix in JSON.
- Do not invent availability rules beyond `status='open'`.
- Match error envelope `{ "error": { "code", "message" } }` used by T2/T4.
- Cite `artifacts/standards/api-cross-cutting.md` (safe 500s, logging).

## 7. Anti-Scope
- No booking creation
- No timezone conversion UI
- No provider-managed availability edits
- No double-booking prevention beyond filtering `booked` status
- No auth
