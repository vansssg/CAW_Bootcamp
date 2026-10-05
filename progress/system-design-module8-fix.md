# System Design Module 08 FIX

Minimal fail: `page=1&page_size=10` with 3 matches returned `total=3` and **0 items** (`ALL_COUNT 0`) because `offset = page * page_size`.

Fix: `offset = (page - 1) * page_size` in `search_memory`. FTS `LIMIT :limit OFFSET :offset` already used that formula; query text stays parameterized (`:q`, allowlisted sort).

Boundary test (`module08_search_fix.py`):

- `FIX_FIRST_PAGE_FULL True` (3/3)
- `FIX_P1_IS_FIRST True`
- `FIX_LAST_PAGE_COUNT 1` `FIX_LAST_IS_LAST True`
- `FIX_PAST_END_COUNT 0 TOTAL 3`
- `FIX_INJECT_SORT_STATUS 400`
- `FIX_FTS_BOUND True`
