# AI-Augmented Engineering Module 04 BUILD — Review Pass

Method: **B pattern-based** first (five categories), then line-by-line on auth/mutation (`createInvitation`, `acceptInvitation`, `persist_invitation_sql`).

`upsk ref review-checklist` loaded. M2/M3 had plans only; `find` at maxdepth 3 showed no invitation app files. Generated first-pass Team Collaboration on this shortener (memory-backed; Postgres/Redis/Docker not serving), then reviewed and patched.

## First-pass measured (before prompts)

`python -m app.scripts.module04_invitation_review_probe`

| Probe | Result |
|-------|--------|
| UNAUTH_STATUS | 401 |
| B_IDOR_CREATE | True (member POST 200) |
| B_ACCEPT_IDOR | True (B accepted A's `new.user@example.com` token, 200) |
| SQL_INTERPOLATED | True (`DROP TABLE` inside concatenated SQL) |
| EMAIL_FAIL_HTTP / STILL_PENDING | 200 / True |
| stdout | `invite email failed ... email= rollback@example.com` |
| INVALID_EMAIL_STATUS | 200 |
| EMPTY_TEAM_NAME_STATUS | 200 |
| SELF_INVITE_STATUS | 200 |
| MISSING_TEAM_STATUS | 404 |
| LOG_LEAKS_EMAIL (emit_log) | False (`[REDACTED_EMAIL]`) |

## File: `api/app/invitations.py`

| Category | Finding | Severity | Evidence |
|----------|---------|----------|----------|
| Security | Create invite: auth only, no owner/admin check | critical | First pass: `B_MEMBER_CREATE_STATUS 200`. `principal-b` is `member` on team 1. |
| Security | Accept invite: any authenticated user with the token | critical | First pass: `B_ACCEPT_IDOR True`, `B_ACCEPTED_BY principal-b`. |
| Security | Email concatenated into SQL | critical | `persist_invitation_sql` built `VALUES ('1', 'x@example.com'; DROP TABLE...')`. Not executed (no Postgres); still merge-blocking. |
| Edge Cases | No email format / empty team name / self-invite / already-member | high | `INVALID_EMAIL_STATUS 200`, `EMPTY_TEAM_NAME 200`, `SELF_INVITE 200`. |
| Error Handling | Email failure left a pending row and printed the address | high | `EMAIL_FAIL_STILL_PENDING True`; stdout leak. Missing team correctly 404. |
| Naming | JS leftovers `createInvitation` / `listInvitations` / `acceptInvitation`; locals `data`/`result` | medium | Function names vs snake_case `create_link` in `main.py`. |
| Tests | One happy-path script; no 403/invalid/email-fail cases | high | `module04_invitation_first_pass_test.py` asserts 200 pending only. |

## File: `api/app/main.py` (invitation routes)

| Category | Finding | Severity | Evidence |
|----------|---------|----------|----------|
| Security | Routes call `require_api_key`; create still logged `email=` | medium | Handler passes raw email; `redact_secrets` turned it into `[REDACTED_EMAIL]`. |
| Edge Cases | Empty `TeamCreate.name` accepted | high | `EMPTY_TEAM_NAME_STATUS 200`. |
| Error Handling | 401 unauth on POST invite | low | `UNAUTH_STATUS 401` — already correct. |
| Naming | `create_team_invitation` wraps `createInvitation` | medium | Two naming styles for one action. |
| Tests | No route tests besides happy path | high | Probe is a review script, not a suite. |

## File: `api/app/scripts/module04_invitation_first_pass_test.py`

| Category | Finding | Severity | Evidence |
|----------|---------|----------|----------|
| Tests | Happy path only; mocks nothing but also covers no deny path | high | Asserts `status == 200` only. Most dangerous untested path: member invite + cross-principal accept. |

## File: `api/alembic/versions/a1b2c3d4e5f6_add_team_invitations.py`

| Category | Finding | Severity | Evidence |
|----------|---------|----------|----------|
| Security | Additive tables; FKs to `teams.id`; no string-built SQL in migration | low | Uses SQLAlchemy `op.create_table`. **Not applied** (`localhost:5432` down). |
| Naming | `principal_id` / `invited_email` match `created_by` string identity | low | Aligns with `links.created_by`, not a `users` UUID table (does not exist). |

Team IDs are integers like `links.id`, not UUIDs. Invalid `team_id` path values 422 via FastAPI. That is consistent with this service, not a UUID bug.

## FIX LIST — Priority Order

1. **[CRITICAL]** IDOR on create — member can invite
   File: `api/app/invitations.py` `createInvitation`
   Fix: `require_team_admin`; 403 if role not owner/admin

2. **[CRITICAL]** SQL interpolation in `persist_invitation_sql`
   File: `api/app/invitations.py`
   Fix: named binds `:team_id`, `:invited_email`; drop `query` from JSON

3. **[HIGH]** No rollback when email fails
   File: `api/app/invitations.py` `createInvitation`
   Fix: pop the row; HTTP 503; do not print email

4. **[CRITICAL]** Accept IDOR — left after prompts 1–3
   File: `acceptInvitation`
   Fix: invitee email must match `PRINCIPAL_EMAIL[principal]`; status must be pending; else 403

## Prompt output review

Prompts 1–3 were applied without rewriting list/accept. Re-probe: `B_IDOR_CREATE False` (403), `SQL_INTERPOLATED False` / `SQL_HAS_BIND True`, `EMAIL_FAIL_HTTP 503`, `EMAIL_FAIL_STILL_PENDING False`. **Accept IDOR still True** — the model only fixed what the prompt named. Prompt 4 then gated accept on email match.

After prompt 4: `B_ACCEPT_A_INVITE_STATUS 403`, `B_ACCEPT_IDOR False`, `B_LEGIT_ACCEPT_STATUS 200` (`b@example.com`).

## Still open (not top-3)

- `INVALID_EMAIL_STATUS 200`, `EMPTY_TEAM_NAME 200`, `SELF_INVITE 200`
- `listInvitations` has no membership check
- camelCase handler names
- Alembic unapplied; SQL helper not executed against Postgres
- Happy-path test file still thin (probe covers deny paths)

`module09_test_suite.py`: 6 tests OK after these routes. No Docker/Railway/Postgres success claimed.
