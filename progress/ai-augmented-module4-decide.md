# AI-Augmented Engineering Module 04 DECIDE

CLI only accepts A|B. Recorded **B pattern_based** as the primary pass.

## Choice: B (pattern-based first)

AI-generated code fails in the same five places the CONTEXT sample did. On this shortener those categories already have measured hits: IDOR 404, `javascript:` 400, `/ready` 503 vs `/live` 200, `page_size` vs `limit` naming, module09 `links.clear()` isolation. A 10-minute standup review of ~400 lines finds more bugs by scanning those five than by reading every line.

## Tradeoff

- **A line-by-line:** complete mental model; 40–60 minutes; catches novel control flow.
- **B pattern-based:** 10–15 minutes; misses bugs that are not auth/validation/errors/naming/tests.

## This service — where line-by-line still happens

Pattern pass on every M2/M3 file. Line-by-line only on high-risk surfaces: `X-API-Key` owner checks, create/PATCH/DELETE, redirect `Location`, search SQL/route order (`/links/search` before `/links/{code}`), invitation SQL and role checks. That is not “hybrid as a hedge”: pattern everywhere, full read only where a wrong line ships a leak or a wrong redirect.

AI reviewing AI is a first pass only. Same training distribution will not catch IDOR the generator missed.

Novel miss pattern-only already caused here: `offset = page * page_size` emptied the first search page (total 3, count 0). That is why the second pass is reserved for mutation and query math, not for every helper.
