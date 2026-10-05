## 1) Authorization rules by action

### Current repository evidence (baseline)
- No request authentication dependency/middleware is wired in `api/app/main.py` (no `Depends(...)`, no token parsing, no role checks).
- `JWT_SECRET` exists only as validated config in `api/app/config.py`, not as request auth logic.
- Even `GET /api/admin/links` is currently unguarded in `api/app/main.py`.
- Invitation endpoints do not exist yet, so all rules below are target-state requirements.

### Proposed authorization matrix
- **Create invitation** (`POST /teams/{team_id}/invitations`)
  - Allowed: team `owner` and `admin`.
  - Denied: non-members, `viewer`, suspended/disabled users.
- **List pending invitations** (`GET /teams/{team_id}/invitations`)
  - Allowed: `owner`, `admin`; optional read for `member` if product requires transparency.
- **Revoke/cancel invitation** (`DELETE /teams/{team_id}/invitations/{invite_id}`)
  - Allowed: invitation creator, team `owner`, or `admin`.
- **Accept invitation** (`POST /invitations/{token}/accept`)
  - Allowed: authenticated user whose identity matches invite target (email/user_id) and invite is `pending`.
- **Reject invitation** (`POST /invitations/{token}/reject`)
  - Allowed: same as accept; also allow inviter/team admin to mark invite rejected only if business wants administrative rejection.
- **Resend invitation** (`POST /teams/{team_id}/invitations/{invite_id}/resend`)
  - Allowed: `owner`/`admin`/inviter; denied once invite is expired/revoked/accepted.

---

## 2) Membership validation rules

- Require `team_members` lookup by `(team_id, actor_user_id)` before any invitation mutation.
- Normalize role model: `owner > admin > member > viewer`.
- Validate team existence first; then membership; then role permission.
- Enforce invitation ownership invariants:
  - `invite.team_id` must equal route `team_id`.
  - `invite.invited_email` or `invite.invited_user_id` must match the accepting/rejecting actor.
  - `invite.status` must be `pending`.
  - `invite.expires_at > now()`.
- Prevent duplicate active invites:
  - Unique constraint recommendation: one active invite per `(team_id, invited_email_or_user_id)`.
- Prevent duplicate membership on accept:
  - If already a member, return conflict/idempotent response (do not create duplicate membership row).
- Require atomic transition on accept/reject:
  - Update invite status with a `WHERE status='pending'` guard to avoid races.

---

## 3) API-level enforcement points

### Current auth entry points and protection gaps
- **Entry points now**: route handlers in `api/app/main.py`.
- **Error handling now**: `HTTPException` global handler returning `{ "detail": ... }` in `api/app/main.py`.
- **Gap**: no auth dependency/middleware currently protects any route.

### Compatible validation hooks for current architecture
- Add a reusable auth dependency function (e.g., `get_current_user`) and attach it with `Depends(...)` on protected routes in `api/app/main.py` (fits current single-file route pattern).
- Add membership/role check helper functions called at start of each invitation handler:
  - `require_team_membership(team_id, user_id)`
  - `require_team_role(team_id, user_id, allowed_roles)`
  - `require_invite_actor_match(invite, actor)`
- Keep authorization checks before DB mutations and before queue side-effects.
- Reuse existing structured logging middleware in `api/app/main.py`:
  - include `req_id`, actor id, team id, invite id, and deny reason for forbidden attempts.
- If async notifications are later added, the existing Redis+worker pattern (`worker/main.py`) can be reused for invite emails/events after authorization succeeds.

---

## 4) Standard error responses

### Current style to preserve
- Continue FastAPI `HTTPException` + global handler style: `{ "detail": "<message>" }` from `api/app/main.py`.

### Recommended status/error model
- **401 Unauthorized**
  - Missing/invalid/expired token.
  - Example detail: `"Authentication required."`
- **403 Forbidden**
  - Authenticated but lacks role or invite ownership.
  - Example detail: `"You are not allowed to perform this action on this team invitation."`
- **404 Not Found**
  - Team or invitation does not exist, or use as anti-enumeration response for cross-team invite IDs.
  - Example detail: `"Invitation not found."`
- **409 Conflict**
  - Duplicate active invite, invite already accepted/rejected/revoked, or membership already exists on accept.
  - Example detail: `"Invitation is no longer actionable."`
- **410 Gone** (optional but useful)
  - Invite expired.
  - Example detail: `"Invitation has expired."`
- **422 Unprocessable Entity**
  - Validation errors (malformed email/token/body), relying on FastAPI validation behavior.

### Consistency rules
- Keep error body shape stable (`detail` string).
- Avoid leaking sensitive internals (do not reveal whether foreign-team invite exists to unauthorized users).
- Use deterministic messages for authorization failures to simplify tests and client handling.

---

## 5) Test scenarios (positive + negative)

### Positive cases
- `owner` creates invite for valid target in same team.
- `admin` creates invite; invite appears in pending list.
- Invited user accepts pending, unexpired invite; membership created; invite marked accepted.
- Invited user rejects pending invite; invite marked rejected.
- Inviter/admin revokes pending invite; invite marked revoked.

### Negative authorization cases
- Unauthenticated user attempts create/accept/reject/revoke -> `401`.
- Team `member`/`viewer` attempts create/revoke invite -> `403`.
- User tries accepting invite issued to another email/user -> `403`.
- User from another team tries to revoke invite by ID -> `404` or `403` per anti-enumeration policy.

### Negative membership/state cases
- Invite create on nonexistent team -> `404`.
- Duplicate active invite for same target/team -> `409`.
- Accept already accepted/rejected/revoked invite -> `409`.
- Accept expired invite -> `410` (or `409` if unified).
- Accept when target already team member -> `409` (or idempotent `200` with no-op contract).

### Concurrency/idempotency cases
- Two simultaneous accept attempts on same invite -> one success, one `409`.
- Accept and revoke race -> exactly one terminal state persists.
- Repeat reject call on already rejected invite -> deterministic `409` (or idempotent no-op if chosen).

### Error-model contract tests
- Every forbidden path returns exact `detail` contract and expected status code.
- Unauthorized/forbidden responses include no sensitive team/invite existence leakage.
- Logging captures deny reason and request correlation id from middleware context.
