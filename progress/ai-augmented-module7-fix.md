# AI-Augmented Engineering Module 07 FIX

AI missed it because it checked membership (is the user on the team?) not purpose (who may change roles). Same miss as GET list: auth present, privilege write unscoped.

## Prompt

`progress/ai-augmented-module7-fix-prompt.md` — six PUT constraints plus the BREAK composition (unique pending email, strip list tokens, accept does not overwrite).

## PUT `/teams/{id}/members/{uid}`

`require_team_admin`, no self-modify, enum + owner-only `owner`, `member.updated` audit.

## Measured (`python -m app.scripts.module07_fix`)

Thirteen cases all OK (`FIX_THIRTEEN_ALL True`). `FIX_AUDIT_MEMBER_UPDATED True`.

BREAK after fix: `BREAK_DUP_PENDING_ALLOWED False` (second invite 409); `BREAK_GET_LIST_TOKEN_LEAK False`; stolen accept 404; role stays viewer; `BREAK_VIEWER_PROMOTED False`. Viewer PUT self admin is now **403** (route exists).

VERIFY still green: owner/superadmin invite 400; `V_PRIVILEGE_ESCALATION False`; `V_CROSS_ALL_DENIED True`; `V_MODULE09_EXIT 0`.
