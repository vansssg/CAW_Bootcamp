# Module 1 DECIDE — review style

Choice: **A inline_comments** (`decisions.module_01.review_style = inline_comments`)

## Why A for authsvc

Auth diffs hide bugs on a single line: `not_owner_status=404` vs 403/200, treating `JWT_SECRET` as an API-key alias, logging the raw `X-API-Key`. A summary that says “error handling needs work” does not tell the author which `return` to change.

If one critical bug is buried in a 200-line, 5-file PR, pinning the comment on that line is the only style that cannot lose it in a paragraph.

## Tradeoff accepted

Risk is death by a thousand paper cuts. Mitigation (not a second recorded choice): write at most 3–5 inline comments, ordered by severity (blocker / should-fix / nit), and open with one sentence that names the theme so the author is not staring at a wall of red. That is combining both in practice; the stored style is still inline because the line pin is the load-bearing part.

## Rejected B for this module

Summary-first is better when the issue is architectural (wrong pipeline). This BUILD is a code review of an auth change, so granularity beats overview.
