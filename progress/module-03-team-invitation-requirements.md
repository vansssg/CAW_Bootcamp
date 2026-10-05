# Module 03 - Team Invitation Requirements (Layered-Surgical)

## Evidence Baseline (Repository Source of Truth)

This requirements spec is grounded only in:
- `api/app/main.py`
- `api/app/models.py`
- `api/app/config.py`
- `api/alembic/versions/6c0d96e3d69b_init_schema.py`
- `api/app/scripts/test_query_columns.py`

Any behavior not directly represented there is marked as **ASSUMPTION**.

## 1) Feature Rules

1. Team invitation APIs must follow existing FastAPI route and handler style.
   - Evidence: routes are declared directly on `app` with decorators in `api/app/main.py`, handlers perform validation/DB work inline, and return JSON-compatible dicts.
2. Request payload validation must use Pydantic request models.
   - Evidence: `LinkCreate` in `api/app/main.py` and settings validation in `api/app/config.py`.
3. Error handling must use `HTTPException` and return FastAPI default JSON error shape (`{"detail": ...}`).
   - Evidence: `HTTPException` usage and custom exception handler returning `{"detail": exc.detail}` in `api/app/main.py`.
4. Database write/read operations must use SQLAlchemy engine with parameterized SQL (`text(...)`, named params).
   - Evidence: `create_link`, `redirect`, and `list_links` database calls in `api/app/main.py`.
5. Schema changes for invitation persistence must include Alembic migration(s) following existing revision layout and explicit upgrade/downgrade index/table operations.
   - Evidence: `api/alembic/versions/6c0d96e3d69b_init_schema.py`.
6. New config knobs (if needed) must be environment-driven and validated through `Settings`.
   - Evidence: strict env validation and exported constants in `api/app/config.py`.
7. Verification artifacts should include at least one deterministic positive/negative check pattern.
   - Evidence: `api/app/scripts/test_query_columns.py` uses explicit assertion pass/fail checks.

## 2) Role/Permission Matrix

No role system for Team Invitation exists in the cited runtime code. The matrix below is therefore **ASSUMPTION** and must be validated before implementation.

| Role | Create invitation | View invitation(s) | Resend invitation | Revoke invitation | Accept invitation |
|---|---|---|---|---|---|
| Team Owner | Allowed | Allowed (team scope) | Allowed | Allowed | Not applicable |
| Team Admin | Allowed | Allowed (team scope) | Allowed | Allowed | Not applicable |
| Team Member | Denied | Denied except own inbound | Denied | Denied | Allowed (own token only) |
| Invitee (not yet member) | Denied | Allowed (own token only) | Denied | Denied | Allowed (own token only) |
| Anonymous | Denied | Denied | Denied | Denied | Denied unless valid acceptance token flow |

Permission guardrails (derived from existing API style + assumptions):
- Unauthorized requests should return `401` (**ASSUMPTION**, no auth middleware is present yet in `api/app/main.py`).
- Forbidden role/action should return `403` (**ASSUMPTION**, status convention not yet implemented in runtime code).
- Not found invitation/team should return `404` (aligned with `Link not found` in `api/app/main.py`).
- Invalid input should return `400` (aligned with existing parameter and URL validation in `api/app/main.py`).

## 3) Invitation State Machine

No invitation lifecycle exists in current models/migrations; this is an explicit **ASSUMPTION** based on standard operational needs.

### States
- `pending` - invitation created and actionable.
- `accepted` - invitee accepted; invitation is terminal.
- `revoked` - inviter/admin invalidated invitation; terminal.
- `expired` - invitation timed out by policy; terminal.

### Allowed Transitions
- `pending -> accepted`
- `pending -> revoked`
- `pending -> expired`
- Terminal states (`accepted`, `revoked`, `expired`) have no outgoing transitions.

### Transition Rules
- Accept is allowed only for `pending` invitations and valid token/identity match (**ASSUMPTION**).
- Revoke is allowed only for `pending` invitations by owner/admin roles (**ASSUMPTION**).
- Expiration is evaluated at acceptance and list/read time using stored expiry timestamp (**ASSUMPTION**).
- Re-accept/revoke of terminal invitations must return conflict-like rejection (`400` or `409`, **ASSUMPTION**; repository currently favors `400` patterns).

## 4) Edge Cases

1. Duplicate active invitation for same team + email/identity.
   - Expected: reject create request.
   - Status: `400` or `409` (**ASSUMPTION**).
2. Attempt to accept invitation that is already accepted/revoked/expired.
   - Expected: reject with clear error detail.
   - Status: `400` (style-consistent default) or `409` (**ASSUMPTION**).
3. Invalid invitation token format or missing token.
   - Expected: reject as bad input.
   - Status: `400` (aligned with existing validation errors in `api/app/main.py`).
4. Unknown invitation identifier.
   - Expected: not found.
   - Status: `404` (aligned with existing not-found handling).
5. Pagination input for invitation listing (`page`, `limit`) less than 1.
   - Expected: reject with same constraint style as admin links list.
   - Status: `400` (aligned with `list_links` behavior in `api/app/main.py`).
6. Database unique/index collisions during create flow.
   - Expected: controlled error response, no partial side effects.
   - Status: `400` or `500` based on classification (**ASSUMPTION**; runtime has no dedicated DB exception mapping).

## 5) External Acceptance Criteria Checklist

Use as pre-merge verification checklist for Team Invitation feature delivery.

### API Contract
- [ ] Invitation create endpoint follows existing FastAPI route style (decorator + function handler).
- [ ] Request payload validation uses Pydantic model(s).
- [ ] Invalid input returns `HTTPException`-backed JSON `{"detail": ...}`.
- [ ] Not-found invitation/team returns `404` with detail message.

### Permission and Security
- [ ] Unauthorized/forbidden paths are explicitly covered (positive and negative role checks).
- [ ] Acceptance path verifies invitation is in `pending` state.
- [ ] Acceptance path rejects invalid/expired/revoked/used invitation tokens.
- [ ] No secrets or static credentials are hardcoded; any new setting is env-driven via `Settings`.

### Data and Migration
- [ ] Invitation persistence schema is introduced via Alembic migration with explicit upgrade/downgrade.
- [ ] Indexing/uniqueness strategy follows migration naming and declaration patterns in existing schema migration.
- [ ] Runtime SQL queries use parameterized SQL (`text` + named bind params), no string interpolation.

### Behavioral Verification (Positive + Negative)
- [ ] Positive: creating a valid invitation returns success payload and persists expected fields.
- [ ] Positive: accepting a valid pending invitation transitions it to `accepted`.
- [ ] Negative: duplicate active invitation is rejected.
- [ ] Negative: invalid paging (`page < 1` or `limit < 1`) is rejected.
- [ ] Negative: accepting expired/revoked/nonexistent invitation is rejected.
- [ ] Deterministic checks are scriptable using assertion-style pattern similar to `api/app/scripts/test_query_columns.py`.

## 6) Assumption Trace (Explicit)

1. **ASSUMPTION:** Team roles (`owner/admin/member/invitee`) exist and are enforceable.
   - Why assumed: no role model or auth middleware appears in `api/app/main.py` or `api/app/models.py`.
2. **ASSUMPTION:** Invitation lifecycle states include `pending/accepted/revoked/expired`.
   - Why assumed: no invitation entities currently exist in model or migration files.
3. **ASSUMPTION:** `401` and `403` are used for authn/authz failures.
   - Why assumed: current code has no auth-protected endpoints, but this is standard HTTP semantics.
4. **ASSUMPTION:** Duplicate invitation protection requires unique constraints and conflict handling.
   - Why assumed: existing schema demonstrates index/uniqueness conventions; invitation-specific constraints are absent.
5. **ASSUMPTION:** Acceptance uses token-based identity verification.
   - Why assumed: invite acceptance needs external claimant verification, but no current implementation exists.
6. **ASSUMPTION:** `400` is preferred over `409` for many validation/state-transition failures unless a conflict policy is explicitly introduced.
   - Why assumed: existing runtime currently uses `400` for invalid request conditions.
