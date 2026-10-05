# System Design Module 08 VERIFY

## What goes wrong if we build SQL with string concatenation?

The client owns the query text. `sort=clicks; DROP TABLE links` or `q=x' OR 1=1` becomes part of the statement. We reject free-form sort (`BAD_SORT_STATUS 400`) and bind `:q` in `plainto_tsquery('english', :q)` — `FTS_PARAM_Q True`. Memory path never interpolates `q` into SQL. Concatenation is how an admin search becomes a write.

## Why must page_size be capped?

Unbounded `LIMIT` is a full scan plus a huge JSON body. `GET /api/admin/links` used to allow any `limit>=1`; `MAX_IN_MEMORY_LINKS` is 10_000. Search rejects `page_size=51` (`HUGE_PAGE_STATUS 400`). Cap is 50. That is the “just add search” outage from CONTEXT, on this process even before Postgres.

## Operational cost of a search engine?

Another cluster to deploy, index, and keep consistent with `POST /links`. Freshness after create would lag. This host already cannot run Docker, Redis, or Postgres — Elasticsearch would be a third down dependency. We chose **A db_native**; runtime is `backend=memory` because `SEARCH_USE_POSTGRES` is unset and 5432 is down. We did not stand up Meilisearch to look complete.
