# Module 1 CONTEXT — Code review as conversation

Scenario: authsvc (X-API-Key on the URL shortener).

## Micro-exercise 1 — worst feedback

Worst pattern I have seen (and sometimes written) is a comment that names a person, not a line: “Why would you do this?” on `require_api_key` when the code already returned 401 for a missing `X-API-Key`. Content was thin (no file, no alternative). Delivery was worse: it read as a character judgment. Google’s 2018 finding matches that: the bar can stay high while the sentence still feels like an attack.

## Micro-exercise 2 — feedback that stuck

Useful feedback on this repo named a concrete alternative: “Return 401/400 at the top of `require_api_key` so the rest of the handler is the success path — we already do that for missing/invalid keys. Not a blocker.” That is specific (function + status codes), suggests the rewrite, and separates style from a bug. Same technical bar, different conversation.

## Compass for this module

Avoid: content-free or personal comments. Produce: specific, alternative-bearing, respectful comments on auth/error-envelope diffs.
