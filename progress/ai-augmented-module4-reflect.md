# AI-Augmented Engineering Module 04 REFLECT

## Counts

First-pass review (before prompts): 3 critical (create IDOR, accept IDOR, interpolated SQL), 5 high (email leftover row + stdout leak, invalid email, empty name, already-member, happy-path-only test), 2 medium (camelCase names, raw `email=` field on emit_log). Real bugs, not style: the three criticals, rollback, and the three VERIFY 400/409 cases. Style: `createInvitation` vs `create_link`.

## IDOR before BREAK?

Yes for POST: first-pass probe `B_IDOR_CREATE True`, then admin gate, VERIFY_4 403. BREAK still found GET list IDOR (`BREAK_GET_LIST_SAW_HIDDEN_EMAIL True`) because the B checklist treated “security” as auth+admin on create, not ownership on every method. Pattern-based missed the gap between two sections the same way line-by-line would miss a missing cross-cut.

## Decision callback (B pattern-based)

The GET IDOR survived because the security pattern asked “does POST have auth?” The route had `require_api_key`, so it passed, even though `listInvitations` took `principal_id` and ignored it. Hybrid’s second pass was supposed to be mutation+auth; list is a read of someone else’s invites and should have been in that high-risk set.

## Personalized checklist

```
[ ] Every method on /teams/{id}/*: auth AND membership/role for that team_id
[ ] Accept: invitee identity match, not just a valid token
[ ] User input: email format, empty name, parameterized SQL only
[ ] Step 2 fails after step 1: email send rolls back the invite row
[ ] Tests: unauth 401, non-admin 403, already-member 409 — not only 200
[ ] IDOR: User B changes team_id (POST and GET) and must not see tokens
```

## Surprise

The code looked like the rest of this FastAPI app. The bugs were the same five categories as the sample `createInvitation`. Clean + predictable is why review is the job.

## PR comment

Blocking: (1) `GET /teams/{team_id}/invitations` returned another team’s invitee emails and raw tokens to any API key — same IDOR as create, different verb. Gate on membership like `require_team_admin`. (2) `acceptInvitation` accepted any principal who held the token; bind to `PRINCIPAL_EMAIL`. (3) Email failure left a pending row and printed the address; delete the row and return 503. Do not merge until outsider GET is 403 and admin POST still creates.

## Knowledge check

1. AI ships the probable pattern (auth middleware). Humans catch domain authorization (this team, this role, this invitee).
2. Biggest decision: B pattern-based, then line-by-line on auth/mutation — and expanding “auth” to every HTTP method after GET leaked.
3. Proof: VERIFY_1 409, VERIFY_2 400, VERIFY_3 401, VERIFY_4 403, VERIFY_5 400; FIX_ADMIN 200 + FIX_NON_ADMIN 403; after list fix outsider GET 403.

Mini VERIFY: `VERIFY_4_MEMBER_NOT_ADMIN_STATUS 403` and `VERIFY_4_NON_MEMBER_STATUS 403`.

Risk: one review pass; list fix could hide teams with 403 vs 404. Mitigation: keep outsider GET 403 and re-run the break probe after each prompt.
