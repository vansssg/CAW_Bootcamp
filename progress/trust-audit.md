## Trust Audit: Architecture Summary

This audit classifies claims from `progress/architecture-summary.md` as TRUST / VERIFY / SUSPICIOUS.

---

## TRUST (directly verified)

### 1) FastAPI app entry point exists in `api/app/main.py`
- **Original claim**: "FastAPI app entry point in `api/app/main.py`."
- **Evidence/source**: `api/app/main.py` contains `app = FastAPI()` and route decorators.
- **Confidence**: **High**
- **Additional check**: `./.venv/Scripts/python.exe -c "import app.main; print('ok')"` to confirm import-time load.

### 2) Models are defined in `api/app/models.py`
- **Original claim**: "Models in `api/app/models.py`."
- **Evidence/source**: `api/app/models.py` defines ORM model classes (`Link`, `ClickEvent`) and table/index metadata.
- **Confidence**: **High**
- **Additional check**: cross-check against Alembic revision in `api/alembic/versions/6c0d96e3d69b_init_schema.py`.

### 3) Listed routes are present in code
- **Original claim**: "Routes listed if directly found in code."
- **Evidence/source**: `api/app/main.py` includes:
  - `@app.get("/health")`
  - `@app.get("/live")`
  - `@app.get("/ready")`
  - `@app.post("/links")`
  - `@app.get("/r/{code}")`
  - `@app.get("/api/admin/links")`
- **Confidence**: **High**
- **Additional check**: run app and call endpoints with curl/HTTP client where runtime dependencies are available.

### 4) Config validation is implemented in `api/app/config.py`
- **Original claim**: "Config validation in `api/app/config.py`."
- **Evidence/source**: `api/app/config.py` uses `pydantic-settings` with required fields and validators (`JWT_SECRET` length, production localhost guard, etc.).
- **Confidence**: **High**
- **Additional check**: run failure-first imports (missing var / invalid value) to confirm validation errors.

### 5) No route-level auth middleware/dependency is currently wired
- **Original claim**: "No implemented authentication/authorization checks on endpoints."
- **Evidence/source**: no `Depends(...)`, auth middleware, or token verification in `api/app/main.py`; admin route has no guard.
- **Confidence**: **High**
- **Additional check**: grep for auth dependencies across app modules and verify none are attached to route handlers.

---

## VERIFY (reasonable inference; needs explicit confirmation)

### 1) Worker consumes Redis queue jobs
- **Original claim**: "Worker consumes Redis queue jobs."
- **Evidence/source**: `worker/main.py` uses `redis.from_url(...)` and `r.brpop("analytics:queue", timeout=5)`.
- **Confidence**: **Medium-High**
- **Additional check**: run worker + push sample Redis job to `analytics:queue`, verify DB write to `analytics` table.

### 2) Worker writes analytics aggregates to Postgres
- **Original claim**: "Worker writes analytics aggregates to Postgres."
- **Evidence/source**: `worker/main.py` executes `INSERT ... ON CONFLICT ...` into `analytics` via psycopg connection.
- **Confidence**: **Medium-High**
- **Additional check**: integration test with live Postgres to verify row creation/update path.

### 3) Request flow includes middleware logging and DB-backed readiness behavior
- **Original claim**: "Request enters logging middleware, handlers run SQL, readiness checks DB."
- **Evidence/source**: middleware and `/ready` SQL check exist in `api/app/main.py`.
- **Confidence**: **Medium**
- **Additional check**: runtime trace/log capture from sample request to confirm execution order end-to-end.

### 4) Team invitation feature should integrate via Redis+worker notifications
- **Original claim**: "Team invitations should use Redis+worker notifications."
- **Evidence/source**: inference from existing async pattern (`analytics:queue`) in `worker/main.py`; no invitation queue exists today.
- **Confidence**: **Medium**
- **Additional check**: architecture decision review to confirm notification mechanism (Redis queue vs alternative event bus/email service).

### 5) New invitation logic should likely be added in `api/app/main.py` first
- **Original claim**: "New routes would currently live in `api/app/main.py`."
- **Evidence/source**: all current routes are centralized there.
- **Confidence**: **Medium**
- **Additional check**: choose whether to preserve current pattern or introduce route/service modules before implementing feature.

---

## SUSPICIOUS (possibly wrong/incomplete/unsupported)

### 1) JWT presence implies auth exists
- **Original claim**: "Authentication exists because `JWT_SECRET` exists."
- **Evidence/source**: `JWT_SECRET` is validated in `api/app/config.py` but no token verification path is used in `api/app/main.py`.
- **Confidence**: **High (suspicious claim)**
- **Additional check**: search for JWT decode/verify usage and auth dependency wiring in request path.

### 2) Admin routes are protected
- **Original claim**: "`/api/admin/links` is protected."
- **Evidence/source**: route is defined with no guard/dependency/middleware in `api/app/main.py`.
- **Confidence**: **High (suspicious claim)**
- **Additional check**: run unauthenticated request against `/api/admin/links`; verify accessibility.

### 3) "Complete auth/authorization layer exists elsewhere"
- **Original claim**: "AuthZ might be implemented in hidden service modules."
- **Evidence/source**: current codebase summary found no controller/service auth modules wired into route execution.
- **Confidence**: **Medium-High (suspicious until proven)**
- **Additional check**: inspect all `api/app/**` modules for guard hooks and confirm they are actually called by route handlers.

---

## Quick conclusion

- **Safe to trust now**: app entrypoint, route inventory, model locations, and config validation mechanics.
- **Needs runtime confirmation**: worker queue behavior and any inferred integration pattern for future invitations.
- **Do not assume**: JWT validation in config means request authentication, or that admin routes are currently protected.

---

## VERIFY command log (Module 1 STEP 4)

### Command 1
- **Command**: `ls c:/UPSK-Bootcamp/api/alembic/versions`
- **Result**:
  - `__pycache__/`
  - `6c0d96e3d69b_init_schema.py`
- **Claim checked**: "There is a migrations folder with revision files."
- **Outcome**: **Confirmed** (supports TRUST-level repository-structure claim).

### Command 2
- **Command**: `rg "Depends\\(|OAuth|Authorization|jwt|JWT|auth" c:/UPSK-Bootcamp/api/app/main.py`
- **Result**: `No matches found`
- **Claim checked**: "Auth/authorization middleware/dependencies protect routes in main API path."
- **Outcome**: **Not supported** in current route module; reinforces SUSPICIOUS classification for implied protection.

### Command 3
- **Command**: `rg "@app\\.get\\(\"/api/admin/links\"\\)" c:/UPSK-Bootcamp/api/app/main.py`
- **Result**: Route declaration found in `api/app/main.py`.
- **Claim checked**: "Admin route exists in current API surface."
- **Outcome**: **Confirmed** route existence; combined with Command 2, no route-level protection evidence found in this file.

### Command 4
- **Command**: `rg "brpop\\(|analytics:queue|from_url\\(|connect\\(" c:/UPSK-Bootcamp/worker/main.py`
- **Result**:
  - `redis_client.from_url(...)`
  - `connect(database_url)`
  - `r.brpop("analytics:queue", timeout=5)`
- **Claim checked**: "Worker consumes Redis queue jobs and is wired to Postgres."
- **Outcome**: **Partially confirmed statically** (code path exists); runtime behavior remains VERIFY until executed in a live stack.

---

## BREAK wrong-claim audit (Module 1 STEP 5)

- **AI-generated claim**:
  - "This starter workspace is only a platform folder with AGENTS.md, CLAUDE.md, reports, and progress/; it has no real application files to test."

- **Why it looked plausible**:
  - The workspace root does contain many management/proof files and progress artifacts, which can mislead an agent that overweights top-level file names.
  - A shallow scan can miss nested application directories (`api/`, `worker/`) and conclude there is no runnable app.

- **Evidence checks performed**:
  1. `ls` at workspace root  
     - Observed `api/`, `worker/`, `infra/`, plus management/proof files.
  2. File-pattern scan (equivalent of card’s file-discovery step):  
     - `rg "(src|packages|routes|models|services|tests|package\\.json)" c:/UPSK-Bootcamp --files-with-matches`
     - Observed many matches including app/runtime-relevant files and tests.
  3. Strongest available sanity check in current workspace:
     - `./.venv/Scripts/python.exe app/scripts/test_query_columns.py` (run from `api/`)
     - Output: `PASS: query uses short_code.`

- **Actual truth from the codebase**:
  - This is **not** only a platform folder. It contains real application code under `api/` and `worker/`, infrastructure definitions under `infra/`, and runnable checks/tests.
  - The environment supports concrete verification work (for example, script-based test pass in `api`).

- **Classification**:
  - **SUSPICIOUS (False claim disproved by command evidence)**.

---

## FIX process improvement (Module 1 STEP 6)

### Policy adopted for future AI-assisted analysis

1. **Treat AI outputs as hypotheses, not facts.**
   - Any architecture or behavior claim from an agent is provisional until checked.

2. **Verify against repository evidence first.**
   - Prefer concrete checks (file listings, targeted search, runnable sanity checks) before accepting conclusions.

3. **Classify before acceptance.**
   - Mark each claim as:
     - **TRUST**: directly verified by source evidence.
     - **VERIFY**: plausible but requires additional confirmation.
     - **SUSPICIOUS**: unsupported, incorrect, or contradicted by evidence.

4. **Record command evidence with outcomes.**
   - Keep a durable audit trail: claim, command, observed output summary, corrected truth, and classification.

### Why this fixes the BREAK failure mode

- The wrong-claim card failure happened because a plausible high-level statement was accepted too quickly.
- This policy prevents that by forcing evidence-based validation and classification before any claim is reused for implementation decisions.
