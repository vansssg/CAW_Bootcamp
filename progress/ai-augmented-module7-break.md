# AI-Augmented Engineering Module 07 BREAK

A viewer promoted themselves. Not through PUT — that route is **404**.

```
viewer accept  --GET list token-->  second pending invite  --accept overwrite-->  member
```

Each piece looked medium. Together they are self-promotion.

## Measured (`python -m app.scripts.module07_break_probe`)

- `PUT /teams/{id}/members/principal-b` `{role:admin}` as B → **404** (`BREAK_PUT_ENDPOINT_ABSENT True`)
- Two pending invites for the same email both **200** (`BREAK_DUP_PENDING_ALLOWED True`)
- Accept viewer → role **viewer**
- GET `/teams/{id}/invitations` as that viewer → **200**, pending row still includes `token` (`BREAK_GET_LIST_TOKEN_LEAK True`)
- Accept stolen pending token → **200**, role **member** (`BREAK_VIEWER_PROMOTED True`)

## Why the audit missed the remaining path

BUILD flagged unconstrained `invite.role` (owner/superadmin). VERIFY allowlisted create to member/viewer, so owner minting is gone. The scanner still marks GET list OK because `require_team_member` exists. It does not look at response shape or at accept overwriting an existing membership.

Composition:

1. Create does not unique pending email
2. List returns raw tokens to any member, including viewer
3. Accept writes `memberships[team,user] = invitation.role` with no “already a member” check

Lesson analog (PUT + isTeamMember + no role enum) is the same pattern: **membership check without privilege check**, plus **unvalidated role write**. Here the write is accept, not PUT.
