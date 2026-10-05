# T5: POST /api/auth/register — create user + optional provider profile

**AI-ready:** Yes  
**Slice:** 2 — User & Provider Identity Ownership  
**Depends on:** T4 (bookings table exists; will link learner_id)

## 1. Title
POST /api/auth/register — register learner/provider identity

## 2. Context (Why)
Slice 2 replaces guest `learner_id` placeholders with real identity. Providers need a linked provider profile row for future listing ownership (Slice 3).

## 3. Scope (What)
- Create `users` and `provider_profiles` tables.
- Implement `POST /api/auth/register` returning a session token (opaque bearer).
- Optional: if `role` includes provider, create `provider_profiles` row keyed to `users.id`.
- File: `api/app/routers/auth.py`, `api/app/models/identity.py`.

## 4. Interface Contract

### Tables
`users`
| column | type | notes |
|--------|------|-------|
| id | UUID PK | |
| email | TEXT UNIQUE NOT NULL | lowercased |
| password_hash | TEXT NOT NULL | bcrypt |
| display_name | TEXT NOT NULL | |
| role | TEXT NOT NULL | `learner` \| `provider` \| `both` |
| created_at | TIMESTAMPTZ NOT NULL | |

`provider_profiles`
| column | type | notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID UNIQUE FK → users.id | |
| headline | TEXT | nullable |
| created_at | TIMESTAMPTZ NOT NULL | |

`sessions`
| column | type | notes |
|--------|------|-------|
| token | TEXT PK | 32+ byte urlsafe |
| user_id | UUID FK → users.id | |
| expires_at | TIMESTAMPTZ NOT NULL | now + 7 days |

### Request
```json
{
  "email": "learner@example.com",
  "password": "string min 8",
  "display_name": "Alex",
  "role": "learner"
}
```
`role` enum: `learner` | `provider` | `both`

### Response `201`
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
When `role` is `provider` or `both`, `provider_profile_id` is a UUID.

### Errors
| status | code |
|--------|------|
| 400 | `invalid_body` |
| 409 | `email_taken` |

### Auth header for later tickets
`Authorization: Bearer <token>`

### Function signature
```python
from sqlalchemy.orm import Session
from app.db import get_db

@router.post("/auth/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse: ...
```
Sync SQLAlchemy only.

## 5. Acceptance Criteria

1. **Given** unused email  
   **When** `POST /api/auth/register` with `role:"learner"`  
   **Then** 201, `user.id` UUID, `token` non-empty, `provider_profile_id` is null

2. **Given** unused email  
   **When** register with `role:"provider"`  
   **Then** 201 and `provider_profile_id` is a UUID present in `provider_profiles`

3. **Given** email already registered  
   **When** register again  
   **Then** 409 with `error.code == "email_taken"`

4. **Given** password length &lt; 8  
   **When** register  
   **Then** 400 with `error.code == "invalid_body"`

## 6. Constraints
- Hash passwords with bcrypt (cost ≥ 10); never store plaintext.
- Emails stored lowercased; uniqueness on lower(email).
- No OAuth/social login.
- Token must be unguessable (`secrets.token_urlsafe(32)`).
- Cite `artifacts/standards/api-cross-cutting.md`: rate limit register (60 rpm), safe errors, log `event=user_registered` with `user_id` only (never password).
- **Authn:** none required to register (public). **Authz:** creating a `provider` role does not grant access to other users' data.
- **Input:** `email` max 320 chars, `display_name` max 80 chars, printable text only (reject `<` `>` to block trivial HTML); `password` 8–128 chars; unknown JSON keys → 400.
- **Data:** UUIDs for ids; `created_at`/`expires_at` ISO-8601 UTC with `Z`.

## 7. Anti-Scope
- No login endpoint beyond register returning token (login can be follow-up)
- No email verification
- No password reset
- No RBAC matrix beyond role string
- No linking historical guest bookings automatically (T6 uses authenticated user id only)
