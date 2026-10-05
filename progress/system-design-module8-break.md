# System Design Module 08 BREAK

Injected medium bug: pagination off-by-one in `search_memory` — `offset = page * page_size` instead of `(page - 1) * page_size`. 1-based `page` was used as a 0-based slice start.

## Symptom (`module08_search_break.py`)

Three `example.com` links, `q=example`, `backend=memory`.

- `page=1&page_size=10`: `ALL_TOTAL 3` but `ALL_COUNT 0` — first page empty because offset=10.
- `page=1&page_size=1`: `P1_SKIPPED_FIRST True` (returned `d8a0682b` / two, not the newest).
- `page=3&page_size=1`: `EMPTY_LAST_WHEN_PAGE_EQ_TOTAL 0` — last page gone.

Not an FTS syntax error (Postgres was not queried). Not injection (`sort` allowlist still 400). The BUILD pause named this class: OFFSET is 0-based, `page` is not.
