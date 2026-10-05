# Module 04 FIX prompt (specific)

In `api/app/invitations.py`, `POST /teams/{team_id}/invitations` already calls `require_api_key` then `require_team_admin`. Keep that. Do not replace it with a TODO or `isAdmin = True`.

Also fix the IDOR found in BREAK: `listInvitations(team_id, principal_id)` ignores `principal_id`. After the team-exists 404, look up `memberships[(team_id, principal_id)]`. If missing, raise `HTTPException(status_code=403, detail="You are not allowed to perform this action on this team invitation.")`. Members (any role) may list. Do not change create/accept/email/SQL helpers.

Verify:
- Owner A POST `/teams/1/invitations` valid new email → 200 (this app uses 200 like POST /links, not 201)
- Member B POST `/teams/1/invitations` → 403
- Non-member B GET `/teams/{A's other team}/invitations` → 403
- Member B GET `/teams/1/invitations` → 200
