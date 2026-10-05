# Module 03 Task 3 - Team Invitation Permission/Membership Validation Plan

## Repository Evidence Used
- `api/app/main.py`
  - FastAPI app and route handlers are defined directly in the entrypoint using function decorators (for example `@app.post("/links")`, `@app.get("/api/admin/links")`).
  - Validation and error behavior currently uses `HTTPException` with `detail` and returns JSON `{"detail": ...}` through the exception handler.
  - Existing guard style is inline checks inside handlers (for example pagination validation in `list_links`).
- `api/app/config.py`
  - Environment-driven settings are validated via `BaseSettings`; security-sensitive values (`jwt_secret`) are required and validated for minimum length.
  - This supports keeping permission logic dependent on configured runtime/auth values, not hardcoded constants.
- `api/app/models.py`
  - Current schema models only `Link` and `ClickEvent` with `ForeignKey("links.id")` and SQLAlchemy declarative style.
  - Relationship and indexing patterns indicate DB-backed ownership and lookup constraints should be explicit and indexed.
- `api/alembic/versions/6c0d96e3d69b_init_schema.py`
  - Migration style uses explicit `op.create_table` and `op.create_index`, with downgrade reversing in dependency-safe order.
  - Confirms the expected source of truth for membership/invitation schema constraints should be Alembic migration plus SQLAlchemy model updates.
- `api/app/scripts/test_query_columns.py`
  - Verification style is lightweight, deterministic assertion checks against concrete expected query fragments.
  - Confirms that permission validation tests should include explicit positive/negative assertions with unambiguous pass/fail signals.

## Assumptions (Explicit)
- **ASSUMPTION 1:** Team membership and invitation tables/routes are not yet implemented in the current runtime files above; this plan defines enforcement behavior to add while preserving current patterns.
- **ASSUMPTION 2:** Authentication identity is available per request at enforcement time (middleware/dependency), but the concrete auth extraction method is not visible in the provided files.
- **ASSUMPTION 3:** Invitation lifecycle states will include at least `pending`, `accepted`, and `revoked` (or equivalent), because permission checks require state-based gating.

## 1) Authorization Rules by Action
- **Create invitation**
  - Allow only team owners/admins (or explicitly permissioned maintainers) to invite.
  - Deny authenticated non-members and lower-privilege members.
- **List invitations for a team**
  - Allow only current team members.
  - Optionally restrict full metadata visibility (inviter identity, internal notes) to elevated team roles.
- **Accept invitation**
  - Allow only the invitee identity bound to the invitation token/id.
  - Deny if invitation is not `pending`, expired, revoked, or already accepted.
- **Revoke invitation**
  - Allow owner/admin/inviter depending on final policy; enforce least privilege and consistent role checks.
  - Deny self-privilege escalation attempts (for example, member revoking owner-created invites without privilege).
- **Remove member / update role**
  - Allow only owner/admin according to final role matrix.
  - Deny changes that would leave the team without required ownership coverage.

## 2) Membership Validation Rules
- Validate membership using DB-backed membership records before every team-scoped invitation action.
- Validate role from persisted membership record (not from client-provided role input).
- Treat invitations as team-scoped resources; every invitation operation must verify `invitation.team_id` matches path/team context.
- Require uniqueness and anti-duplication checks:
  - No duplicate pending invitation for same `team_id + invitee`.
  - Do not create invitation if invitee already has active membership in team.
- On invitation acceptance, perform transactional membership creation + invitation state transition to prevent split-brain states.
- Ensure membership checks use indexed lookup patterns consistent with existing query-specific verification discipline.

## 3) API-Level Enforcement Points
- Apply authorization/membership checks inside request handlers at the same layer where current validation is performed (`api/app/main.py` route-handler pattern), unless an existing shared dependency pattern is introduced by current project conventions.
- For each team-invitation endpoint, enforce in this order:
  1. Authenticated identity present.
  2. Target team/invitation exists.
  3. Membership and role authorization for action.
  4. Invitation state preconditions.
  5. Mutating DB operation (transactional where multi-step).
- Keep failure behavior consistent with current FastAPI usage:
  - Raise `HTTPException` with precise `detail`.
  - Rely on existing `http_exception_handler` response shape (`{"detail": ...}`).
- Keep environment/security constraints aligned with `api/app/config.py`:
  - No hardcoded secrets.
  - Any token/JWT/invite-signature validation should read from environment-backed settings.

## 4) Standard Error Responses
Use existing error envelope pattern observed in runtime code:
- Response shape: `{"detail": "<message>"}` (via `HTTPException` and global handler).

Recommended status/detail mapping for invitation and membership checks:
- `401 Unauthorized`
  - `detail`: authentication required / invalid token.
  - Use when requester identity is missing/invalid.
- `403 Forbidden`
  - `detail`: insufficient team permissions / not a member / action not allowed for role.
  - Use when identity exists but lacks required access.
- `404 Not Found`
  - `detail`: team not found / invitation not found.
  - Use when targeted resource does not exist (or is intentionally hidden by policy).
- `409 Conflict`
  - `detail`: duplicate pending invitation / already a member / invitation already accepted.
  - Use for state conflicts during create/accept flows.
- `422 Unprocessable Entity` (or existing validation equivalent)
  - `detail`: invalid payload fields (email/role/state transition input).
- `400 Bad Request`
  - `detail`: malformed action or invalid state transition when semantic input is invalid.

## 5) Test Scenarios (Positive + Negative)
Follow existing repository verification style: explicit deterministic assertions and query/behavior checks.

### Positive Scenarios
- Owner/admin successfully creates invitation for non-member.
- Team member with allowed visibility lists team invitations.
- Invitee accepts valid pending invitation and becomes team member.
- Authorized actor revokes pending invitation successfully.
- Membership lookup returns expected allow/deny for role matrix actions.

### Negative Scenarios
- Unauthenticated request to invitation endpoints returns `401`.
- Non-member attempting to create/list/revoke invitations returns `403`.
- Member without required role attempts restricted action and gets `403`.
- Accept invitation with wrong identity (not invitee) returns `403`.
- Accept revoked/expired/already-accepted invitation returns `409` (or policy-specific `400/404`, but must be consistent).
- Create invitation for existing team member returns `409`.
- Create duplicate pending invitation for same invitee/team returns `409`.
- Team mismatch between route team and invitation team returns `403` or `404` per resource-hiding policy.

### Regression/Safety Checks
- Existing non-invitation routes (`/health`, `/live`, `/ready`, `/links`, `/r/{code}`, `/api/admin/links`) preserve current behavior and response schema.
- Error responses for new invitation checks remain consistent with `{"detail": ...}`.
- Any new DB constraints/indexes for membership/invitation flows follow SQLAlchemy + Alembic patterns from `models.py` and `6c0d96e3d69b_init_schema.py`.

