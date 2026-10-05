# Module 03 Build - Task 2: Team Invitation Schema Plan

## 1) Schema Proposal

### Proposed table: `team_invitations`

Purpose: store invite lifecycle records for adding users to teams.

Columns (proposed):

- `id` - `Integer`, primary key.
- `team_id` - `Integer`, foreign key to `teams.id`, `nullable=False`.
- `invited_email` - `String`, `nullable=False`.
- `invited_by` - `String`, `nullable=False` (matches existing string-based actor tracking pattern).
- `invite_code` - `String`, `nullable=False`.
- `status` - `String`, `nullable=False` (expected values: `pending`, `accepted`, `revoked`, `expired`).
- `expires_at` - `DateTime`, `nullable=False`.
- `accepted_at` - `DateTime`, `nullable=True`.
- `created_at` - `DateTime`, `nullable=False`, `server_default=func.now()`.

Repository evidence:

- `api/app/models.py` uses SQLAlchemy declarative models with `Integer` PKs and `String` fields (`Link`, `ClickEvent`).
- `api/app/models.py` uses `DateTime` + `server_default=func.now()` (`ClickEvent.clicked_at`), which supports the same pattern for `created_at`.
- `api/alembic/versions/6c0d96e3d69b_init_schema.py` creates tables with `sa.Column(...)` and explicit nullability, matching this proposal style.

ASSUMPTIONS:

- A1: A `teams` table exists (or is created in a separate task) so `team_id -> teams.id` can be enforced.
- A2: No dedicated `users` table relationship is required for inviter identity in this task, so `invited_by` remains `String` (aligned with existing `created_by` usage).

## 2) Relationship Map

Primary relationship:

- `teams (1) -> (many) team_invitations` via `team_invitations.team_id`.

Operational relationship (non-FK, by convention):

- inviter identity tracked as `team_invitations.invited_by` string (same style as `links.created_by`).

Repository evidence:

- `api/app/models.py` shows FK relationship pattern (`click_events.link_id -> links.id`) and string actor pattern (`links.created_by`).
- `api/alembic/versions/6c0d96e3d69b_init_schema.py` shows migration-level FK declaration style (`sa.ForeignKey("links.id")`).

ASSUMPTION:

- A3: Invitation acceptance will be processed by application logic, not DB triggers/procedures.

## 3) Constraints and Indexes

Required constraints/indexes:

- Unique index on `invite_code`:
  - Name: `ix_team_invitations_invite_code`
  - Uniqueness: `unique=True`
- Non-unique index on `team_id` for lookup/filter:
  - Name: `ix_team_invitations_team_id`
- Composite index for stateful admin queries:
  - Name: `ix_team_invitations_team_id_status`
  - Columns: `team_id`, `status`
- Optional uniqueness guard (business rule dependent):
  - Unique composite index: `team_id`, `invited_email`
  - Use only if one active invite per email per team is required by product behavior.

Repository evidence:

- `api/app/models.py` defines indexes in `__table_args__` using `Index(...)` with explicit names.
- `api/alembic/versions/6c0d96e3d69b_init_schema.py` creates indexes separately via `op.create_index(...)`, including unique and composite patterns.
- `api/app/main.py` shows conflict-aware write pattern (`ON CONFLICT`) that benefits from deterministic unique keys (`short_code` today, `invite_code` for invitations).

ASSUMPTION:

- A4: Partial indexes/check constraints are intentionally not introduced because current baseline migrations only use table/foreign-key/index primitives.

## 4) Migration Steps

1. Add SQLAlchemy model in `api/app/models.py`:
   - Create `TeamInvitation(Base)` with `__tablename__ = "team_invitations"`.
   - Follow existing field declarations and `__table_args__` index declaration style.
2. Create a new Alembic revision under `api/alembic/versions/`:
   - Add `op.create_table("team_invitations", ...)`.
   - Add `op.create_index(...)` calls for all defined indexes.
   - Add `op.drop_index(...)` and `op.drop_table(...)` in `downgrade()` in reverse order.
3. Keep DB integration path unchanged:
   - Existing runtime flow in `api/app/main.py` performs DB operations through `engine` and SQL text execution.
   - Invitation handlers should follow this same request -> handler -> SQL pattern when implemented in a later task.
4. Preserve environment-driven configuration:
   - No secrets or connection literals in migration/model files; rely on `api/app/config.py` + existing engine wiring.

Repository evidence:

- `api/alembic/versions/6c0d96e3d69b_init_schema.py` shows the exact expected migration lifecycle and downgrade ordering.
- `api/app/main.py` shows runtime DB writes/reads through `engine.begin()` / `engine.connect()`.
- `api/app/config.py` enforces environment-based configuration and rejects invalid runtime settings.

## 5) Validation Checklist

Positive checks:

- Migration applies cleanly (`upgrade`) and creates `team_invitations` with expected columns.
- Migration rollback (`downgrade`) removes indexes first, then table.
- Unique `invite_code` is enforced at DB level.
- FK `team_id` rejects non-existent team references (if `teams` exists as assumed).
- Query paths by `team_id` and `(team_id, status)` use indexes.

Negative checks:

- Insert with duplicate `invite_code` fails.
- Insert with `NULL` in required fields (`team_id`, `invited_email`, `invited_by`, `invite_code`, `status`, `expires_at`) fails.
- Insert with invalid `team_id` fails FK validation.
- Rollback does not leave orphan index objects.

Regression guards:

- Existing `links` and `click_events` behavior remains unchanged.
- Existing startup readiness checks and logging in `api/app/main.py` remain unaffected.
- Existing environment validation behavior in `api/app/config.py` remains unaffected.
