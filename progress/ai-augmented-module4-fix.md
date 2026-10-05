# AI-Augmented Engineering Module 04 FIX

Wrote a specific prompt (file, endpoint, membership lookup, 403, do-not-refactor). Applied `require_team_member` in `listInvitations`. Create already used `require_team_admin` (owner or admin, not a `isAdmin = True` placeholder).

Required tests (`python -m app.scripts.module04_invitation_fix_probe`):

| Case | Expected | Actual |
|------|----------|--------|
| Admin A POST invite | 201 (lesson) / 200 this app | **200** pending (same as POST /links) |
| Non-admin B POST invite | 403 | **403** |
| Outsider B GET A's other team list | 403 | **403**, hidden email not visible |

Re-ran BREAK probe: `BREAK_GET_LIST_B_STATUS 403`, `BREAK_GET_LIST_SAW_HIDDEN_EMAIL False`.
