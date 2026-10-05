# System Design Module 08 REFLECT

## Chosen strategy + why

**A `db_native`.** Module 02 is PostgreSQL. Admin substring/tag/sort must be fresh after `POST /links`. Elasticsearch would be another cluster; Docker, Redis, and Postgres are already down here. Tradeoff: no fuzzy match; `ILIKE`/FTS can scan — capped at `page_size=50`. Runtime was `backend=memory` (`SEARCH_USE_POSTGRES` unset). GIN SQL is in `api/app/sql/links_fts.sql` but was not applied to 5432.

The off-by-one is exactly the callback: building search on a store not designed as a search engine means we own OFFSET math and parameterized FTS ourselves.

## One security rule

Never concatenate user input into SQL (or into an ORDER BY). `sort=clicks;drop` → 400. FTS uses `plainto_tsquery('english', :q)`. Tags are `[a-z0-9-]{1,32}`. Owner scope: `B_LEAKED False`.

## Pagination lesson

`offset = page * page_size` made `page=1&page_size=10` return 0 items with `total=3`. Fix `(page-1)*page_size`: first page 3/3, last page 1, page=4 empty with total 3.

`progress/state.json` next: Module 09 context.
