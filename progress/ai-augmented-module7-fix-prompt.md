# Module 07 FIX prompt

There is no working PUT yet (BREAK measured 404). Privilege write is still `acceptInvitation` plus GET list tokens.

## PUT /teams/{team_id}/members/{user_id}

In `api/app/invitations.py` add `update_member_role`. Mount PUT in `main.py`. Constraints:

1. `require_team_admin` (owner/admin). Viewer/member → 403. Do not use member-only.
2. If `user_id` equals requester → 403 `Cannot modify your own role.`
3. Role allowlist: `admin|member|viewer`. Empty/`superadmin` → 400. Owner requester may also set `owner`.
4. Admin requester setting `owner` → 403 `Only owners can create other owners.`
5. Publish `member.updated` with team_id, target_user_id, old_role, new_role, author_id (requester).
6. Target missing → 404. Team missing → 404.

Do not change link ownership 404s or invite email match.

## Close the BREAK composition (same privilege write)

- One pending invite per team+email → 409
- `listInvitations` omits `token`
- `acceptInvitation` if already a member → 409, do not overwrite role

Tests: thirteen PUT cases in `module07_fix.py`; BREAK probe must show `BREAK_VIEWER_PROMOTED False`.
