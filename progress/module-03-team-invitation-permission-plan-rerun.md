### 1) Authorization Rules by Action

- **Create short link (`POST /links`)**  
  - **Current evidence:** endpoint accepts request body and validates URL scheme; no auth gate is present in runtime code.  
  - **Policy plan:** enforce authenticated actor check before create (future), then allow create only for authenticated users.  
  - **Error convention:** when denied, raise `HTTPException` so response stays `{"detail":"..."}`.

- **Redirect short link (`GET /r/{code}`)**  
  - **Current evidence:** publicly reachable in current runtime; not membership-scoped.  
  - **Policy plan:** keep public read unless business rules require private links later.  
  - **Error convention:** missing resource already uses `HTTPException(status_code=404, detail="Link not found")`.

- **List admin links (`GET /api/admin/links`)**  
  - **Current evidence:** route exists with pagination validation but no auth/membership checks.  
  - **Policy plan:** enforce admin-only permission at API boundary before query execution.  
  - **Error convention:** use `HTTPException` for denials/validation failures to preserve `{"detail":"..."}`.

---

### 2) Membership Validation Rules

- **Tenant/team membership check before protected actions**  
  - **ASSUMPTION:** future team-based behavior should require membership validation prior to mutation or admin listing.
- **Membership source of truth**  
  - **ASSUMPTION:** membership table/model is not present in provided evidence files, so validation storage contract is currently undefined.
- **Validation ordering**  
  - first authenticate actor, then verify membership/role, then run endpoint business logic.
- **Failure handling**  
  - membership/role failures should be raised via `HTTPException` to keep envelope identical (`{"detail":"..."}`), not custom wrappers.

---

### 3) API-Level Enforcement Points

- **Route-level guards (primary point)**  
  - Add permission/membership checks at start of protected handlers (`POST /links`, `GET /api/admin/links`) before DB writes/reads.
- **Validation branch consistency**  
  - Existing input validation already uses `HTTPException` (`page/limit`, URL scheme); keep same pattern for permission/membership denials.
- **Central exception behavior**  
  - `api/app/main.py` has `@app.exception_handler(HTTPException)` returning `JSONResponse(..., content={"detail": exc.detail})`; all enforcement should route through this.
- **Config grounding for auth readiness**  
  - `api/app/config.py` requires `jwt_secret`; this supports future auth integration, but no active auth middleware is evidenced in allowed files.
- **Schema constraints that indirectly support membership checks**  
  - `links.created_by` exists in model and migration; can be used as ownership signal (**ASSUMPTION** for future membership policy).

---

### 4) Standard Error Responses

- **Strict required envelope (evidenced):** `{"detail":"..."}` only.  
- **Strict required mechanism (evidenced):** raise `HTTPException(...)` and rely on `api/app/main.py` handler.  
- **Do not introduce alternate formats:** no `{"error":...}`, no `{"status":"error"}`, no nested custom envelope.  
- **Evidenced runtime status codes from allowed files:**  
  - `400` (invalid URL scheme; invalid pagination inputs)  
  - `404` (link not found on redirect)  
- **ASSUMPTION-only future codes (separated):**  
  - `401` for unauthenticated  
  - `403` for authenticated but unauthorized / non-member  
  - `409` for invitation/state conflicts  
  - `422` for richer semantic validation paths beyond current 400 usage

---

### 5) Test Scenarios (Positive + Negative)

- **Positive**
  - valid `POST /links` with `http/https` returns created payload.
  - valid `GET /r/{code}` returns redirect and analytics upsert path executes.
  - valid `GET /api/admin/links?page=1&limit=10` returns paginated list.
  - query column convention remains `short_code`-based (aligned with `test_query_columns.py` and schema/model fields).

- **Negative**
  - `POST /links` with non-http(s) URL returns `400` and body `{"detail":"Only http and https URLs are allowed."}`.
  - `GET /r/{missing}` returns `404` and body `{"detail":"Link not found"}`.
  - `GET /api/admin/links` with `page<1` or `limit<1` returns `400` and `{"detail":"page and limit must be positive integers"}`.
  - **ASSUMPTION future auth tests:** unauthenticated protected call -> `401` with `{"detail":"..."}`.
  - **ASSUMPTION future membership tests:** authenticated non-member/non-admin call -> `403` with `{"detail":"..."}`.
  - **ASSUMPTION future invitation conflict tests:** duplicate/invalid invite transition -> `409` with `{"detail":"..."}`.

---

### Repository Evidence Used

- `api/app/main.py`
- `api/app/config.py`
- `api/app/models.py`
- `api/app/scripts/test_query_columns.py`
- `api/alembic/versions/6c0d96e3d69b_init_schema.py`

---

### Assumptions

- Auth middleware/dependency wiring is not present in the allowed evidence set; any JWT enforcement path is assumed future work.
- Team/membership persistence model is not present in the allowed evidence set; membership contract details are assumed.
- `401/403/409/422` are not evidenced in current runtime code from the allowed files and are proposed only as future-policy assumptions.
