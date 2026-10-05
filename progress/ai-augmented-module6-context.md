# AI-Augmented Engineering Module 06 CONTEXT

Parallel agents are multiple crews on one building. Fast if the LEGO studs match. Catastrophic if they do not.

## Why this module exists

M4 review and M5 iteration were one stream. M6 splits Team Collaboration (comments, members, activity) across agents. The hidden lesson from M2 is still the lesson: decomposition is interface contracts, not just task lists.

## What already is a contract in this repo

- Auth: `X-API-Key` → `principal-a` / `principal-b`; missing key **401**.
- Team writes: `require_team_admin` → **403** for member B on team 1.
- Team reads: `require_team_member` → outsider GET list **403** (M4 BREAK/FIX).
- Activity events: `{type, team_id, ts, payload}` with **no email** (`ITER_NO_EMAIL_IN_PAYLOAD True`).
- Invitations: memory store; Postgres **not** serving; do not invent a `users` UUID table.

If three agents run without those locks, one will log emails, one will skip membership, one will NOTIFY on INSERT while 5432 is down.

## Minimum contract vs over-spec

Lock: event shape, auth helper names, status codes (401/403/409), “no PII in payload,” in-memory like `links`. Do not lock comment CSS or exact function names inside a file.

## Merge risk we already felt

GET list ignored `principal_id` while POST create used `require_team_admin`. Same resource, two “agents,” two auth stories. Interface-first would have said: every `/teams/{id}/*` method calls the same membership helper.
