# Module 07 — System security/architecture findings

Hybrid scan + human critical path. Scanner would mark POST invite OK (`require_team_admin` exists). Human tried `role=owner`.

## Auth map (generated team surface)

| Endpoint | Auth | Authorization | Status |
|----------|------|-----------------|--------|
| POST /teams | require_api_key | any authenticated | OK |
| POST /teams/{id}/invitations | require_api_key | require_team_admin | OK for identity; **CRITICAL** role not allowlisted |
| GET /teams/{id}/invitations | require_api_key | require_team_member | OK (membership) |
| POST /invitations/{token}/accept | require_api_key | email match + pending | OK identity; writes `invitation.role` blindly |
| WS /ws/teams/{id}/activity | header API key | require_team_member | OK |
| POST/GET /teams/{id}/comments | require_api_key | require_team_member | OK |
| PATCH/DELETE comments | require_api_key | member + author | OK (admins cannot moderate — REVIEW) |
| GET /teams/{id}/audit | require_api_key | require_team_member | REVIEW (any member reads audit) |
| PUT /teams/{id}/members/{uid} | — | — | **missing**; privilege path is invite.role instead |

## Input validation

| Input | Validation | Status |
|-------|------------|--------|
| team name | non-empty strip | OK (400) |
| invite email | EMAIL_FORMAT | OK |
| invite role | **none** | **CRITICAL** `superadmin` stored |
| comment body | 1-5000 | OK |

## Measured privilege escalation

`python -m app.scripts.module07_security_scan`

- SCAN_B_INVITE_OWNER_STATUS **403** (member cannot invite)
- SCAN_A_INVITE_OWNER_STATUS **200** role=owner
- SCAN_B_ACCEPT_OWNER_STATUS **200**; SCAN_B_ROLE_AFTER_ACCEPT **owner**; SCAN_PRIVILEGE_ESCALATION **True**
- SCAN_ROLE_SUPERADMIN_STATUS **200** stored `superadmin`

Impact: an owner can mint another owner (or arbitrary role string) via invite. Analog of the lesson’s PUT member without admin+enum.

## Other findings

| Sev | Cat | Description | Fix plan |
|-----|-----|-------------|----------|
| Critical | Security | Invite `role` unconstrained; accept writes memberships[role] | Allowlist `member`/`viewer`; reject `owner`/`admin`/`superadmin` |
| High | Data integrity | Accept has no pending CAS | Only transition if status==pending in one assignment (already checked, still racy in-process) |
| Medium | Security | GET audit is any member | Document or require admin |
| Medium | Architecture | `createInvitation` camelCase vs `create_link` | Rename later |
| Low | Test | No test that role=owner is 400 | Add with the allowlist |
| Low | Deps | No new PyPI packages for comments/audit/mentions | Keep stdlib |

## Architecture

Routes in `main.py` like links. Errors still `{error:{code,message,request_id}}`. Events no email (`audit` pops email). SQL helper uses binds. No httpx. Postgres not serving; no live FK races.

## Secrets

No hardcoded API keys in generated team files. Invite JSON still returns `token` to the creating admin (needed to accept in tests). `emit_log` redacts emails.

Critical fix is in this module (FIX step): role allowlist. Do not treat scanner OK as owner-checked.
