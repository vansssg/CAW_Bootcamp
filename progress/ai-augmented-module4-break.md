# AI-Augmented Engineering Module 04 BREAK

Symptom: a non-admin could act on a team they do not manage. POST create is now 403 (`BREAK_POST_IDOR_BLOCKED True`). The same URL-trust bug is still on **GET**.

`listInvitations(team_id, principal_id)` takes `principal_id` and never uses it. Any authenticated card opens any room.

Measured (`python -m app.scripts.module04_invitation_break_probe`):

- A creates team 2 `secret-team` and invites `hidden.user@example.com`
- B POST create to team 2 → **403**
- B GET `/teams/2/invitations` → **200**, count 1, saw hidden email **True**, saw token **True**

IDOR surface: `GET /teams/{team_id}/invitations`. Hotel-key analogy still holds for list: valid API key, wrong team, door opens.
