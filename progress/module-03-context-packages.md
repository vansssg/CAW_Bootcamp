# Module 03 BUILD - Context Packages

This document records the layered-surgical context bundles used for the first-pass runs.

## Task 1 - Team Invitation Requirements

### Files to Read (and omission risk)
- `api/app/main.py` - without it, API/route/response patterns can drift.
- `api/app/models.py` - without it, entity and relationship conventions can drift.
- `api/app/config.py` - without it, environment/security constraints can be missed.
- `api/alembic/versions/6c0d96e3d69b_init_schema.py` - without it, migration/schema conventions can drift.
- `api/app/scripts/test_query_columns.py` - without it, verification style and deterministic checks can be missed.

### Files to Modify
- none

### Expected Output
- `progress/module-03-team-invitation-requirements.md`

## Task 2 - Team Invitation Schema/Migration Plan

### Files to Read (and omission risk)
- `api/app/models.py` - without it, model field/relationship conventions can drift.
- `api/alembic/versions/6c0d96e3d69b_init_schema.py` - without it, migration structure/constraints can drift.
- `api/app/main.py` - without it, runtime DB integration assumptions can drift.
- `api/app/config.py` - without it, DB/env constraints can be missed.

### Files to Modify
- none

### Expected Output
- `progress/module-03-team-invitation-schema-plan.md`

## Task 3 - Permission and Membership Validation Plan

### Files to Read (and omission risk)
- `api/app/main.py` - without it, route/auth/error integration points can drift.
- `api/app/config.py` - without it, auth/config constraints can be missed.
- `api/app/models.py` - without it, membership checks may not match relationship conventions.
- `api/app/scripts/test_query_columns.py` - without it, verification style may drift.
- `api/alembic/versions/6c0d96e3d69b_init_schema.py` - without it, schema assumptions for membership/invitations can drift.

### Files to Modify
- none

### Expected Output
- `progress/module-03-team-invitation-permission-plan.md`
