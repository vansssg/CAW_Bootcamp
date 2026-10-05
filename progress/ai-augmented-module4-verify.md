# AI-Augmented Engineering Module 04 VERIFY

ASGI only (`python -m app.scripts.module04_invitation_review_probe`). Never opened DATABASE_URL. Postgres/Redis/Docker not claimed up.

| Test | Expected | Actual |
|------|----------|--------|
| 1 Invite existing member `b@example.com` to team 1 | 409 or 400 | **409** `Already a team member` |
| 2 POST /teams `{name:""}` and `{name:" "}` | 400 | **400** / **400** |
| 3 POST invite, no auth | 401 | **401** |
| 4 User B invite to A's team | 403 | **403** member-not-admin on team 1; **403** non-member on team 2 |
| 5 `{email:"not-an-email"}` | 400 | **400** |

All five failed on first-pass (200s except unauth 401). After BUILD prompts 1–4 plus VERIFY follow-ups for member/name/email, all five pass.

Also still true: `B_ACCEPT_IDOR False`, `B_LEGIT_ACCEPT_STATUS 200` on a new team, `EMAIL_FAIL_HTTP 503` with no leftover row, `SQL_HAS_BIND True`.
