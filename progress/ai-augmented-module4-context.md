# AI-Augmented Engineering Module 04 CONTEXT

Tied 38% with Decomposition; this skill is next (established order after System Design). Practitioner M4 CONTEXT. No code this step.

## Five failures in the sample `createInvitation`

1. **Security:** `teamId` and `email` interpolated into SQL (`'${teamId}'`). Any authenticated user can invite to any team — no membership/admin check (IDOR). Log line leaks emails.

2. **Edge cases:** No email format/empty/null check. No “already a member,” self-invite, or invalid `teamId`.

3. **Error handling:** `catch` logs `err` and returns `"Something went wrong"`. Email send after INSERT has no rollback — dangling invitation.

4. **Naming:** `createInvitation` also emails. `team` is `SELECT *` used as `team.name`. `invitation` is raw query output.

5. **Tests:** One happy-path test. Same mock for lookup and insert. Asserts 201 only. No 401, invalid email, missing team, injection, or email-failure cases.

## Same five on this URL shortener (already measured)

| Category | Evidence in this repo |
|----------|------------------------|
| Security | IDOR: B GET/PATCH/DELETE of A’s code is **404** (`NOT_OWNER_STATUS`). Empty API key on `/links/search` is **401**. |
| Edge | `javascript:alert(1)` create **400**. Search `page_size=51` **400**. Pagination off-by-one (`offset=page*size`) made first page empty (`total 3, count 0`) until FIX. |
| Errors | `/ready` **503** with `database=disconnected`; `/live` **200**. Envelope `{error:{code,message,request_id}}`. |
| Naming | `process_job` vs persist vs DLQ is specific; older `processData`-style risk is `list_links` `limit` vs search `page_size`. |
| Tests | `module09_test_suite.py` six cases; shared-state flake `4 != 0` without `links.clear()`. |

Postgres/Redis/Docker still not serving — not claimed otherwise.
