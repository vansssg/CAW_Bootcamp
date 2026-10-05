## 1) Schema proposal

### `team_invitations` (new table)

> **Assumption A1 (uncertain):** `users`, `teams`, and `team_memberships` tables already exist (or will be introduced before this migration in the same release train). This repository currently does not contain them, so FK targets and key types are inferred.

- `id` — `INTEGER PRIMARY KEY` (aligned with existing `links.id`, `click_events.id` pattern)
- `team_id` — `INTEGER NOT NULL` (FK to `teams.id`)
- `invited_email` — `VARCHAR NOT NULL` (destination identity)
- `invited_email_normalized` — `VARCHAR NOT NULL` (lowercased/trimmed copy for uniqueness and lookups)
- `invited_user_id` — `INTEGER NULL` (FK to `users.id`, nullable until account exists or is matched)
- `invited_by_user_id` — `INTEGER NOT NULL` (FK to `users.id`, inviter identity)
- `role` — `VARCHAR NOT NULL` (intended team role on acceptance; e.g. `admin|member|viewer`)
- `token` — `VARCHAR NOT NULL` (opaque acceptance token)
- `status` — `VARCHAR NOT NULL` (lifecycle: `pending|accepted|revoked|expired`)
- `expires_at` — `TIMESTAMPTZ NOT NULL` (invite validity cutoff)
- `accepted_at` — `TIMESTAMPTZ NULL`
- `revoked_at` — `TIMESTAMPTZ NULL`
- `accepted_membership_id` — `INTEGER NULL` (FK to `team_memberships.id`, points to resulting membership row)
- `created_at` — `TIMESTAMPTZ NOT NULL DEFAULT now()`
- `updated_at` — `TIMESTAMPTZ NOT NULL DEFAULT now()`

> **Assumption A2 (uncertain):** `team_memberships` uses `INTEGER` PK. If memberships use UUID, `accepted_membership_id` and related FKs should match that type exactly.

---

## 2) Relationship map

- `team_invitations.team_id` -> `teams.id` (many invitations per team)
- `team_invitations.invited_by_user_id` -> `users.id` (one inviter can create many invitations)
- `team_invitations.invited_user_id` -> `users.id` (optional pre-linked recipient user)
- `team_invitations.accepted_membership_id` -> `team_memberships.id` (0..1 mapping after acceptance)
- Logical lifecycle:
  - `pending`: created, not accepted/revoked/expired
  - `accepted`: `accepted_at` set, `accepted_membership_id` expected non-null
  - `revoked`: `revoked_at` set
  - `expired`: status transition when `expires_at < now()` (done by app/job)

---

## 3) Constraints/indexes

### Core constraints
- FK constraints:
  - `fk_team_invitations_team_id`
  - `fk_team_invitations_invited_user_id`
  - `fk_team_invitations_invited_by_user_id`
  - `fk_team_invitations_accepted_membership_id`
- Check constraints:
  - `ck_team_invitations_status` -> `status IN ('pending','accepted','revoked','expired')`
  - `ck_team_invitations_role` -> `role IN ('admin','member','viewer')`  
    > **Assumption A3 (uncertain):** these are the canonical role values.
  - `ck_team_invitations_accept_fields` -> if `status='accepted'`, then `accepted_at IS NOT NULL`
- Uniqueness:
  - `uq_team_invitations_token` on `token`

### Duplicate / active-invite prevention strategy
Use DB-enforced prevention of parallel active invites for same team+recipient:

- Partial unique index on normalized identity while active:
  - `uq_team_invites_active_team_email`
  - columns: `(team_id, invited_email_normalized)`
  - predicate: `status = 'pending'`
- Optional companion unique index when recipient account is known:
  - `uq_team_invites_active_team_user`
  - columns: `(team_id, invited_user_id)`
  - predicate: `status = 'pending' AND invited_user_id IS NOT NULL`

This allows re-inviting after prior invite is `accepted|revoked|expired`, while hard-blocking duplicate live invitations.

### Supporting indexes
- `ix_team_invitations_team_status` on `(team_id, status)`
- `ix_team_invitations_invited_user_status` on `(invited_user_id, status)`
- `ix_team_invitations_expires_at` on `(expires_at)` for expiry sweeps
- `ix_team_invitations_created_at` on `(created_at)` for listing/audit

---

## 4) Migration steps

> Forward-only plan, no destructive changes, no unrelated schema edits.

1. **Create new Alembic revision** using existing style  
   Suggested name: `add_team_invitations` (final filename will include generated revision ID, e.g. `<rev>_add_team_invitations.py`).

2. **Create `team_invitations` table** with all columns above, including defaults and nullability.

3. **Add FK constraints** to `teams`, `users`, and `team_memberships`.  
   - If those tables are guaranteed present before this revision, create FKs immediately.
   - If not guaranteed, split into two forward migrations:
     - Migration N: create table + non-FK columns/indexes
     - Migration N+1: add FKs once parent tables exist  
   > **Assumption A4 (uncertain):** migration ordering across features is controlled and deterministic.

4. **Add constraints** (`status`, `role`, acceptance consistency, token uniqueness).

5. **Add indexes** (including partial unique active-invite indexes) after table creation.

6. **No backfill needed** for existing data because table is new and additive.

7. **Deploy order recommendation**:
   - Run migration
   - Deploy API logic that writes both `invited_email` and `invited_email_normalized`
   - Enable invitation endpoints
   - Add scheduled expiry updater (or API-side expiry transitions) to move stale `pending` invites to `expired` for long-term index hygiene.

---

## 5) Validation checklist

- [ ] Alembic revision follows current project convention (`api/alembic/versions/<revision>_<slug>.py`)
- [ ] `upgrade()` is additive only; no drops/renames of existing objects
- [ ] All FK column types exactly match referenced PK types (`INTEGER` vs UUID)
- [ ] `token` uniqueness is enforced at DB layer
- [ ] Partial unique index blocks duplicate active invites per team+recipient
- [ ] Same recipient can be invited again after prior invite leaves `pending`
- [ ] `status` and `role` check constraints reject invalid values
- [ ] Query paths are index-covered (`team + status`, `user + status`, expiry sweep)
- [ ] Expiry handling path is defined (`pending` -> `expired`) so active uniqueness remains semantically correct
- [ ] No unrelated schema changes are included in this migration
