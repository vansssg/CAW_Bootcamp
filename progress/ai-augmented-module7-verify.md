# AI-Augmented Engineering Module 07 VERIFY

Targeted fix prompt: `progress/ai-augmented-module7-fix-prompt.md`

There is no `PUT /teams/:id/members/:uid`. Privilege path is `POST /teams/{id}/invitations` `role` written on accept.

## Fix applied

`INVITE_ROLES = frozenset({"member", "viewer"})` after `require_team_admin`. Invalid role → 400. Stored/published `role_norm`.

Regression caught: replacing `ADMIN_ROLES` with `INVITE_ROLES` made `require_team_admin` NameError → HTTP **500** on invite (`SCAN_B_INVITE_OWNER_STATUS 500`, `V_OWNER_ROLE_STATUS 500`, `V_MEMBER_ROLE_STATUS 500`). Restored both constants. Fix-the-fix before recheck.

## Recheck (`python -m app.scripts.module07_security_scan`)

- Auth: B invite owner **403**; A invite owner **400** (was 200)
- Input: `role=superadmin` **400**; stored None (was 200/`superadmin`)
- Privilege: `SCAN_PRIVILEGE_ESCALATION False` (was True)
- IDOR: outsider still cannot create on team 1 as member-not-admin

## Recheck (`python -m app.scripts.module07_verify`)

- `V_OWNER_ROLE_STATUS 400`
- `V_SUPERADMIN_ROLE_STATUS 400`
- `V_MEMBER_ROLE_STATUS 200`
- `V_ACCEPT_MEMBER_STATUS 200`
- `V_B_ROLE member`
- `V_PRIVILEGE_ESCALATION False`
- Cross-team (B on A's secret team): invite **403**, comment **403**, audit **403**, list **403**; `V_CROSS_ALL_DENIED True`
- `V_MODULE09_EXIT 0`

Postgres/Redis/Docker not used. ASGI `call()` only.
