# Module 03 System-Level Context (Reusable)

## 1) Architecture & Application Flow
- Follow FastAPI entrypoint and route organization in `api/app/main.py`.
- Preserve current request -> handler -> database interaction flow.
- Do not introduce new architecture layers unless required by existing project patterns.

## 2) Data Model & Database Conventions
- Follow model and relationship patterns in `api/app/models.py`.
- Use Alembic migration style from `api/alembic/versions/6c0d96e3d69b_init_schema.py`.
- Avoid unrelated schema modifications.

## 3) API Contract & Response Patterns
- Follow existing endpoint naming, HTTP method, and handler conventions.
- Keep response and error handling behavior consistent with runtime patterns.
- Preserve current validation/input handling style.

## 4) Configuration & Security Constraints
- Use environment-driven runtime settings from `api/app/config.py`.
- Do not hardcode secrets or environment-specific values.
- Preserve validation and security guardrails already present in config/runtime.

## 5) Testing & Verification Rules
- Use existing tests/scripts as behavior references.
- Validate expected behavior with positive and negative scenarios.
- Ensure proposals do not regress existing functionality.
