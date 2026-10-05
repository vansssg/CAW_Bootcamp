# Module 03 VERIFY - Convention Matching

Scope: compare first-pass Task 1/2/3 outputs against existing repository conventions (not correctness of final feature design).

Repository convention anchors used:
- `api/app/main.py`
- `api/app/models.py`
- `api/app/config.py`
- `api/alembic/versions/6c0d96e3d69b_init_schema.py`

## Task 1 Output Review
Target: `progress/module-03-team-invitation-requirements.md`

### 3 things that match conventions
1. Uses FastAPI/Pydantic/HTTPException language consistent with route + validation patterns in `api/app/main.py`.
2. Uses parameterized SQL expectation (`text(...)` + named params), matching DB interaction style in `api/app/main.py`.
3. Grounds schema evolution in Alembic upgrade/downgrade flow, matching `6c0d96e3d69b_init_schema.py`.

### 1 thing that does not fully match (or remains ambiguous)
- Error-status policy is not fully aligned: output alternates between `400` and `409` conflict handling as assumptions, while current runtime conventions demonstrate clear `400`/`404` but no established `409` policy.

### Likely missing context that would reduce mismatch
- A concrete source file or test suite defining conflict/status-code policy for business-state transitions (currently absent in repo).

---

## Task 2 Output Review
Target: `progress/module-03-team-invitation-schema-plan.md`

### 3 things that match conventions
1. Uses SQLAlchemy type conventions (`Integer`, `String`, `DateTime`) consistent with `api/app/models.py`.
2. Uses explicit index naming and migration sequencing conventions consistent with `6c0d96e3d69b_init_schema.py`.
3. Keeps migration-first schema change planning and avoids proposing unrelated dependencies, consistent with current stack.

### 1 thing that does not fully match (or remains ambiguous)
- Proposes FK to `teams.id`, but no `teams` table exists in current models/migration baseline, so this cannot be validated against existing conventions and remains assumption-heavy.

### Likely missing context that would reduce mismatch
- Existing `teams`/`memberships` model+migration files (not present yet), or explicit product contract defining those foundational tables first.

---

## Task 3 Output Review
Target: `progress/module-03-team-invitation-permission-plan.md`

### 3 things that match conventions
1. Enforces `HTTPException` + `{"detail": ...}` error envelope, matching the global exception handler in `api/app/main.py`.
2. Keeps request-layer validation/enforcement at route-handler level, matching current inline guard pattern in `api/app/main.py`.
3. Preserves env-driven security constraints and no hardcoded secrets, matching `api/app/config.py`.

### 1 thing that does not fully match (or remains ambiguous)
- Introduces richer status mapping (`401/403/409/422`) that is sensible but not yet demonstrated by existing invitation/auth routes in current runtime code; therefore partially assumption-driven.

### Likely missing context that would reduce mismatch
- A real authenticated/authorized route module in this codebase showing established `401/403/409/422` behavior and role-resolution patterns.

---

## Overall Verify Outcome
- Context packages produced outputs that mostly match repository style for framework, migration structure, error-envelope shape, and DB interaction patterns.
- Main mismatch source is not naming/layout drift, but missing baseline feature/auth artifacts in repo, which forces policy-level assumptions (roles, conflict codes, invitation states).
- No fixes applied in this step (VERIFY only); mismatches are recorded for BREAK/FIX handling.

## Non-code-change confirmation
- This VERIFY step produced documentation only.
- No application implementation files were modified.
