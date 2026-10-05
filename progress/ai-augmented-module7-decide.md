# AI-Augmented Engineering Module 07 DECIDE

CLI A|B. Recorded **B ai_assisted_hybrid**.

First pass: mechanical scan — every `/teams` and `/invitations` route has `require_api_key`; writes use `require_team_admin` or author check; events have no `email` key; SQL uses binds. Then **manual critical path**: invite create/accept, comment mutate, audit PII, WS membership.

**Tradeoff vs A:** This repo is small enough to read every file. A still failed us on GET list after POST looked authed (attention, not skill). B’s blind spot is “check exists but checks the wrong object” — same training distribution as the generator (M4: AI reviewing AI). That is why the human hour is call chains, not utils.

**This service:** `require_api_key` on POST invite did not imply owner. Hybrid: scanner finds missing `require_*`; human traces `team_id` in the URL to `memberships[(team_id, principal)]`.
