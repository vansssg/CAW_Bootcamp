# T2: GET /api/providers — list seeded providers

**AI-ready:** Yes  
**Slice:** 1 — Browse and Book (Seeded Provider)  
**Depends on:** T1

## 1. Title
GET /api/providers — list seeded providers with basic info

## 2. Context (Why)
Learners need a marketplace list of providers before picking a service/slot. This is the first read API for Slice 1.

## 3. Scope (What)
- Implement `GET /api/providers` returning JSON array of providers joined with their primary service summary.
- File: `api/app/routers/providers.py` (or match existing router layout); register on app router with prefix `/api`.
- Read-only; no auth.

## 4. Interface Contract

### Request
- Method: `GET`
- Path: `/api/providers`
- Query: none required
- Headers: `Accept: application/json`

### Response `200`
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

### Response `500`
```json
{ "error": { "code": "internal_error", "message": "string" } }
```

### Function signature (prescriptive)
```python
from sqlalchemy.orm import Session
from app.db import get_db  # add yield helper in app/db.py if missing (see T4)

@router.get("/providers")
def list_providers(db: Session = Depends(get_db)) -> ProviderListResponse: ...
```

`ProviderListResponse` and nested models in `api/app/schemas/providers.py`. Sync SQLAlchemy only (match `SessionLocal`).

## 5. Acceptance Criteria

1. **Given** T1 seed completed  
   **When** `GET /api/providers`  
   **Then** status is 200 and `providers` length is 3

2. **Given** T1 seed completed  
   **When** `GET /api/providers`  
   **Then** each item includes `id`, `display_name`, `category`, `city`, and nested `service.id` / `service.price_cents`

3. **Given** empty providers table  
   **When** `GET /api/providers`  
   **Then** status is 200 and `providers` is `[]`

## 6. Constraints
- FastAPI + sync SQLAlchemy (`SessionLocal` / `get_db`); do not introduce asyncio DB drivers.
- JSON only; camelCase keys are forbidden — use snake_case as above.
- Use existing DB session dependency; do not open a second engine.
- Pagination not required.
- Cite `artifacts/standards/api-cross-cutting.md` (safe errors, logging). Read-only GET may omit auth; still no stack traces on 500.

## 7. Anti-Scope
- No search, filter, sort, or category query params
- No ratings fields
- No auth
- No POST/PUT/DELETE providers
- No slots in this response
