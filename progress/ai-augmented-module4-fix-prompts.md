# Follow-up prompts (top 3) — Module 04 BUILD

Ran against `api/app/invitations.py` only. Did not ask for a full-file rewrite.

## Prompt 1 — Create IDOR

In `api/app/invitations.py`, function `createInvitation`, any authenticated principal can invite to team 1. `principal-b` is role `member` on team 1 and currently gets HTTP 200 (`B_IDOR_CREATE True`).

Change only the authorization gate at the start of `createInvitation`: look up `memberships[(team_id, principal_id)]`. If the role is not `owner` or `admin`, raise `HTTPException(status_code=403, detail="You are not allowed to perform this action on this team invitation.")`. Do not change accept/list in this prompt. Fixed means: `X-API-Key` of principal-b posting to `/teams/1/invitations` returns 403 and no new invitation row.

## Prompt 2 — Interpolated SQL

In `persist_invitation_sql`, `team_id` and `email` are concatenated into the SQL string (`SQL_INTERPOLATED True` with payload `x@example.com'; DROP TABLE teams;--`). The string is also returned on the JSON body as `query`.

Replace `persist_invitation_sql` with a helper that returns `(sql, params)` using named bind placeholders `:team_id` and `:invited_email` only. Stop putting `query` on the invitation response. Do not execute Postgres; localhost:5432 is down. Fixed means the returned SQL contains no raw email and no single-quoted payload.

## Prompt 3 — Email rollback

When `INVITE_EMAIL_FAIL=1`, `createInvitation` still stores a `pending` row and returns HTTP 200 (`EMAIL_FAIL_STILL_PENDING True`). `print(..., email=)` also leaked the address on stdout.

If `send_invitation_email` raises, delete the invitation just inserted and raise `HTTPException(status_code=503, detail="invitation email failed")`. Do not print or log the raw email. Fixed means: no leftover row for that email, HTTP 503, outbox empty.

## Prompt 4 — Accept IDOR (found on re-review after prompts 1–3)

Prompts 1–3 did not touch `acceptInvitation`. Re-probe after those fixes: `B_ACCEPT_IDOR True` (`principal-b` accepted A's invite for `new.user@example.com`, HTTP 200).

In `acceptInvitation` only: after the invitation is found, compare the invitee's email to `PRINCIPAL_EMAIL[principal_id]` (casefold/strip). If they differ, or the invite is not `pending`, raise 403. Do not add the acceptor as a member on failure. Fixed means: B accepting A's `new.user@example.com` token returns 403; B accepting a pending invite whose email is `b@example.com` returns 200 and membership is `member`.

