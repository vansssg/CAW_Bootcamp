## Folder structure

- `api/` — primary backend service (FastAPI app, config, DB setup, models, migrations, containerization): `api/app/main.py`, `api/app/config.py`, `api/app/db.py`, `api/app/models.py`, `api/alembic.ini`, `api/alembic/versions/6c0d96e3d69b_init_schema.py`, `api/Dockerfile`, `api/requirements.txt`.
- `worker/` — separate background worker process that consumes Redis jobs and writes analytics aggregates to Postgres: `worker/main.py`.
- `infra/` — local infrastructure definitions (Postgres + Redis via Docker Compose): `infra/docker-compose.yml`.
- `.github/workflows/` — CI pipeline for lint + script-based tests in `api`: `.github/workflows/ci.yml`.
- `progress/` and root `*.json` proof files — learning/progress artifacts, not runtime app code: `progress/module-01-diagnosis.md`, `module3-report.json` (representative).

## Backend structure

- **Framework**: FastAPI app with Uvicorn runtime: `api/app/main.py`, `api/Dockerfile`.
- **Entry points**:
  - API process: FastAPI app object `app = FastAPI()` and Uvicorn command in container `uvicorn app.main:app`: `api/app/main.py`, `api/Dockerfile`.
  - Worker process: infinite loop in `worker/main.py` consuming Redis queue.
- **Configuration layer**: Pydantic settings from `.env`, strong validation for required env vars/port/JWT/production localhost checks: `api/app/config.py`, `api/.env.example`.
- **Controllers/routes/services**:
  - No dedicated controller/service folders.
  - Route handlers are defined directly in `api/app/main.py`.
  - Data access is inline SQL via SQLAlchemy `text(...)` in route handlers.
- **Request flow**:
  - HTTP request enters FastAPI middleware for structured logging and request ID.
  - Route handler validates input (Pydantic/body or query), executes SQL against Postgres via shared engine, returns JSON or redirect.
  - Exceptions are normalized by a global HTTPException handler.
  - Startup hook verifies DB connectivity and ensures `analytics` table exists.
  - References: `api/app/main.py`, `api/app/db.py`.

## Data models

- **ORM entities (defined in code)**: `api/app/models.py`
  - `Link` (`links`): `id`, `short_code`, `original_url`, `created_by`; indexes on `short_code` (unique) and `created_by`.
  - `ClickEvent` (`click_events`): `id`, `link_id` (FK to `links.id`), `clicked_at`; compound index on `(link_id, clicked_at)`.
- **Migration-defined schema**: `api/alembic/versions/6c0d96e3d69b_init_schema.py`
  - Creates `links` and `click_events` with same key fields and indexes.
- **Runtime-created table (not in migration)**: `analytics` table is created during app startup with FK to `links(id)` and unique `(link_id, timestamp_bucket)`: `api/app/main.py`.
- **Relationships**:
  - One `Link` to many `ClickEvent` rows via `click_events.link_id`.
  - One `Link` to many `analytics` hourly buckets via `analytics.link_id`.
  - References: `api/app/models.py`, `api/alembic/versions/6c0d96e3d69b_init_schema.py`, `api/app/main.py`.

## API routes

Defined in `api/app/main.py`:

- `GET /health` — basic health probe; output `{ "ok": true }`.
- `GET /live` — liveness probe; output `{ "ok": true }`.
- `GET /ready` — readiness probe with DB check (`SELECT 1`); output `{ "ok": true }` or server error if DB unavailable.
- `POST /links`
  - Input: JSON body `{ "long_url": "<string>" }` via `LinkCreate`.
  - Behavior: validates URL scheme (`http|https`), upserts into `links`, logs creation.
  - Output: `{ "short_code": "abc123", "long_url": "<input>" }`.
  - Errors: `400` for invalid scheme.
- `GET /r/{code}`
  - Input: path param `code`.
  - Behavior: looks up `links`, upserts hourly `analytics` count, redirects.
  - Output: HTTP `307` redirect to `original_url`.
  - Errors: `404` if short code not found.
- `GET /api/admin/links`
  - Input: query params `page` (default `1`), `limit` (default `10`), both must be positive.
  - Behavior: paginated select from `links`.
  - Output: `{ page, limit, count, items }`.
  - Errors: `400` for invalid pagination values.

## Authentication and authorization

- **Current state**: No implemented authentication middleware/dependencies or authorization checks on endpoints.
  - Routes are publicly callable, including `GET /api/admin/links`: `api/app/main.py`.
- **Config intent present but unused**:
  - `JWT_SECRET` is required/validated in settings, but not consumed by request auth logic: `api/app/config.py`.
  - `CORS_ORIGIN` is configured but not applied through CORS middleware in app setup: `api/app/config.py`, `api/app/main.py`.
- **Implication**: Authorization boundaries are not enforced at route level in current backend code.

## Database layer

- **Technology**:
  - PostgreSQL + psycopg driver.
  - SQLAlchemy engine/sessionmaker for API process.
  - Redis used for worker queueing.
  - References: `api/requirements.txt`, `api/app/db.py`, `worker/main.py`, `infra/docker-compose.yml`.
- **Connection/configuration**:
  - Environment-driven config (`DATABASE_URL`, `REDIS_URL`) validated by Pydantic settings: `api/app/config.py`, `api/.env.example`.
  - Shared SQLAlchemy engine initialized in `api/app/db.py`.
- **Migrations**:
  - Alembic configured (`api/alembic.ini`, `api/alembic/env.py`) with one initial revision creating `links` and `click_events`: `api/alembic/versions/6c0d96e3d69b_init_schema.py`.
- **Data access patterns**:
  - API uses raw SQL text queries directly in route handlers, not repository/service abstractions: `api/app/main.py`.
  - Worker uses direct psycopg cursor SQL and Redis `BRPOP` loop for async aggregation work: `worker/main.py`.
  - Mixed schema management pattern: part via Alembic migrations, part via runtime `CREATE TABLE IF NOT EXISTS` in startup hook (`analytics`): `api/app/main.py`.

## Team collaboration feature context

Likely integration points for a **team invitation** feature:

- **Models/entities**:
  - Add new entities (e.g., `teams`, `team_members`, `team_invitations`) alongside current ORM models: `api/app/models.py`.
  - Add corresponding Alembic revisions (instead of startup SQL) in `api/alembic/versions/`.
- **Routes/endpoints**:
  - New API endpoints would currently live in `api/app/main.py` (existing pattern), e.g. team creation/invite acceptance/list membership.
  - If scaling, introducing a route/module split would be a natural refactor because `main.py` is already carrying middleware + all handlers.
- **Services/business logic**:
  - No current service layer; invitation lifecycle logic (token generation, expiry, accept/revoke flows) would either be added inline (current pattern) or motivate first extraction into `app/services/*` (new pattern).
- **Permissions/authorization**:
  - Critical gap: authn/authz is absent.
  - Team invites require introducing JWT verification and role checks (owner/admin/member) before protected team routes; config primitives already exist (`JWT_SECRET`) in `api/app/config.py`.
- **Notifications/async processing**:
  - Existing async substrate is Redis + worker queue (`analytics:queue`) in `worker/main.py`.
  - Invitation notifications (email/push/webhook) could reuse this pattern with a dedicated queue + worker handler.
- **Database and audits**:
  - Invitation audit/event tracking can follow `analytics`/`click_events` style time-based records, but should be migration-managed (Alembic) for consistency: `api/alembic/*`, `api/app/main.py`.
