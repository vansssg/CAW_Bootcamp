## 1) Feature rules

### 1.1 Domain and architecture fit
- Team Invitation is a new feature domain; no current team/invitation models or routes exist in runtime code (`api/app/models.py`, `api/app/main.py`).
- Current API routing style is centralized route handlers in one module, with inline SQL access (`api/app/main.py`), so invitation endpoints should follow this pattern unless a refactor is intentionally introduced.
- ASSUMPTION: Invitation data will be migration-managed (Alembic) rather than startup-time `CREATE TABLE` to avoid mixed schema ownership (`api/alembic/versions/6c0d96e3d69b_init_schema.py`, `api/app/main.py`).

### 1.2 Identity and auth baseline
- Current app validates presence of `JWT_SECRET` in config but does not apply auth middleware/dependencies to routes (`api/app/config.py`, `api/app/main.py`).
- `GET /api/admin/links` is currently unguarded, indicating no active authorization boundary in route execution (`api/app/main.py`).
- ASSUMPTION: Invitation feature requires introducing authenticated user context before role checks can be enforced (because no request auth pipeline currently exists).

### 1.3 Invitation lifecycle states
- `pending`: invite created and usable.
- `accepted`: recipient accepted; membership created; invite no longer usable.
- `rejected`: recipient explicitly declined; invite no longer usable.
- `expired`: invite reached expiry timestamp; invite no longer usable.
- `revoked` (applicable): inviter/admin invalidated pending invite; invite no longer usable.
- Terminal states: `accepted`, `rejected`, `expired`, `revoked` (no transitions out).

### 1.4 Who can send invites
- Intended sender roles: `team_owner`, `team_admin`.
- Disallowed sender roles: `team_member`, `team_viewer`, unauthenticated users.
- ASSUMPTION: Team role model will include owner/admin/member/viewer as referenced in team-collaboration scope artifacts (`ai-augmented-engineering-module1-scenario-pick-proof.json`).

### 1.5 Who can accept/reject
- Accept/reject actor must be the intended recipient identity of that invite.
- ASSUMPTION: Recipient identity is bound to an authenticated principal (email/account) and validated on accept/reject.
- If actor does not match recipient identity, operation fails with authorization error.

### 1.6 Expiry and invalidation rules
- Invite has `expires_at` set at creation.
- On any accept/reject/revoke attempt, system must verify invite is still `pending` and `now < expires_at`.
- Expired invites are non-recoverable; accepting or rejecting after expiry fails and preserves `expired`.
- Revocation can only target `pending` invites; revoking terminal invites is a no-op or conflict failure (implementation choice).
- Any invite for a user who becomes team member before acceptance is invalidated from acceptance path (treated as already-member conflict).

### 1.7 Uniqueness and duplication
- ASSUMPTION: Only one active (`pending`) invite per `(team_id, recipient_identity)` is allowed.
- Duplicate invite creation behavior:
  - if existing `pending` invite exists and not expired/revoked: conflict or idempotent return of existing invite.
  - if previous invite is terminal (`expired/revoked/rejected/accepted`): creation allowed as new invite.

---

## 2) Role/permission matrix

| Actor Role | Create Invite | Revoke Invite | View Invite Status | Accept Invite | Reject Invite |
|---|---|---|---|---|---|
| Unauthenticated | Deny | Deny | Deny | Deny | Deny |
| Team Owner | Allow | Allow | Allow (team scope) | Deny (unless also recipient) | Deny (unless also recipient) |
| Team Admin | Allow | Allow (team scope) | Allow (team scope) | Deny (unless also recipient) | Deny (unless also recipient) |
| Team Member | Deny | Deny | Deny or limited self-view | Deny (unless recipient) | Deny (unless recipient) |
| Team Viewer | Deny | Deny | Deny or limited self-view | Deny (unless recipient) | Deny (unless recipient) |
| Invite Recipient (matching identity) | Deny | Deny | Allow (self invite) | Allow if `pending` and unexpired | Allow if `pending` and unexpired |

Notes:
- ASSUMPTION: “matching identity” is resolved from authenticated principal, not only token possession.
- ASSUMPTION: Team owner/admin boundaries are implemented at API layer with role lookup against team membership tables (not present yet in current code).

---

## 3) Invitation state machine

### States
`pending` -> (`accepted` | `rejected` | `expired` | `revoked`)

### Transitions

| From | Event | Guard | To | Side Effects |
|---|---|---|---|---|
| pending | Recipient accepts | actor matches recipient, not expired, recipient not already member | accepted | create team membership; mark invite terminal |
| pending | Recipient rejects | actor matches recipient, not expired | rejected | mark invite terminal |
| pending | Expiry job/check | `now >= expires_at` | expired | mark invite terminal |
| pending | Owner/Admin revokes | actor has revoke permission | revoked | mark invite terminal |
| pending | Recipient accepts but already member | membership exists | pending (no transition) -> return failure | reject action with already-member conflict |
| accepted/rejected/expired/revoked | Any accept/reject/revoke | terminal state | no transition | return invalid-state failure |

Implementation notes based on current architecture:
- Since no background scheduler exists for invitation expiry in current API code, expiry can be enforced lazily on read/action (evaluate `expires_at` at operation time) and optionally by async worker later (`worker/main.py` pattern).
- ASSUMPTION: If tokenized links are used, token lookup maps uniquely to invite row and state checks happen server-side.

---

## 4) Edge cases

- **Duplicate pending invite**
  - Condition: same team + same recipient has active pending invite.
  - Expected: prevent duplicate active invite; return conflict/idempotent existing invite.
- **Already-member acceptance**
  - Condition: recipient is already a team member when accepting.
  - Expected: fail with already-member; invite should not create duplicate membership.
- **Invalid recipient**
  - Condition: recipient identity not resolvable/invalid format/nonexistent user.
  - Expected: invite creation fails validation (or records external-email invite only if product permits).
  - ASSUMPTION: Whether non-registered emails are allowed is unknown.
- **Expired link**
  - Condition: accept/reject after `expires_at`.
  - Expected: fail with expired-invite response; no membership changes.
- **Revoked invite usage**
  - Condition: recipient attempts accept/reject after revoke.
  - Expected: fail with revoked-invite response.
- **Invite replay**
  - Condition: accept endpoint called repeatedly after first success.
  - Expected: first call succeeds; subsequent calls fail as terminal-state operations.
- **Unauthorized actor**
  - Condition: non-owner/admin sends or revokes; non-recipient accepts/rejects.
  - Expected: authorization failure; no state mutation.
- **Race: accept vs revoke**
  - Condition: concurrent accept and revoke requests.
  - Expected: exactly one terminal transition succeeds; enforce atomic update by state guard (`WHERE state='pending'` semantics).
- **Race: accept vs expiry boundary**
  - Condition: accept at expiry timestamp edge.
  - Expected: deterministic rule (`now >= expires_at` is expired) and consistent response.
- **Data consistency**
  - Condition: invite accepted but membership insert fails.
  - Expected: transactional behavior; no partial state (invite remains pending or operation fully rolled back).

---

## 5) External acceptance criteria checklist

- [ ] Unauthenticated caller cannot create/revoke/accept/reject invites.
- [ ] Owner/admin can create invite for recipient on their team.
- [ ] Member/viewer cannot create invites.
- [ ] Recipient can accept own pending, unexpired invite.
- [ ] Recipient can reject own pending, unexpired invite.
- [ ] Non-recipient cannot accept/reject invite.
- [ ] Accepting invite creates membership exactly once.
- [ ] Duplicate active invite creation is blocked or idempotently returns existing invite.
- [ ] Accepting already-member invite fails with clear conflict response.
- [ ] Expired invite cannot be accepted or rejected.
- [ ] Revoked invite cannot be accepted or rejected.
- [ ] Revocation works only for authorized roles and only while invite is pending.
- [ ] Terminal invites (`accepted/rejected/expired/revoked`) cannot transition again.
- [ ] Concurrent accept/revoke results in a single winning terminal transition, with no split-brain outcome.
- [ ] All failure responses are explicit and distinguish invalid state vs unauthorized vs invalid recipient.
- [ ] Invitation state transitions are auditable (who acted, when, from->to).
- [ ] Expiry behavior is deterministic at boundary timestamps.
- [ ] Specified role boundaries are enforced by server-side checks, not client behavior.

### Assumption trace (explicit)
- ASSUMPTION: Role taxonomy includes owner/admin/member/viewer for teams.
- ASSUMPTION: Invite recipient identity can be securely matched to authenticated principal.
- ASSUMPTION: One active invite per `(team_id, recipient_identity)` uniqueness rule.
- ASSUMPTION: Team/member/invite persistence tables will be introduced via Alembic migration pattern.
- ASSUMPTION: Non-registered email invite behavior is product-defined and currently unknown.
