# System Design Module 08 BUILD

`GET /links/search` is registered **before** `/links/{code}` so `search` is not a short code. Auth is `X-API-Key` (Module 04 A). Owner-scoped. `page_size` default 10, max **50**, values `>50` or `page<1` → 400 (reject, not silent clamp). Metadata: `page`, `page_size`, `total`. `sort` allowlist `created_at|clicks`, `order` `asc|desc`. Tags `[a-z0-9-]{1,32}`.

Postgres FTS is parameterized (`plainto_tsquery('english', :q)` + GIN on generated `search_tsv`) in `api/app/sql/links_fts.sql` and `app/search.py`. Runtime used **memory** because `SEARCH_USE_POSTGRES` is unset and `localhost:5432` is down — we did not wait ~4s per search or claim a GIN build.

## Evidence (`module08_search_verify.py`)

- CREATE A 200×3, B 200×1
- UNAUTH 401
- page_size=51 → 400 `page_size must be <= 50`
- sort=`clicks;drop` → 400
- q=example as A: total **3** (includes `other.example.org` substring), owners `{principal-a}`, `B_LEAKED False`, backend `memory`
- tag=docs total **2**
- page=1&page_size=1 and page=2: each 1 item, different codes, total 3
- page=0 → 400
- FTS SQL contains `:q` and `plainto_tsquery`

## Why pagination off-by-one is common

APIs are 1-based (`page=1` is the first page). SQL `OFFSET` is 0-based. The formula is `offset = (page - 1) * page_size`. Using `OFFSET page` skips the first page. Using `page=0` as “first page” while the server treats `page<1` as invalid (we 400) is the other direction. Empty last pages happen when `offset >= total` — `total` in the body is how clients detect that, not a 404.
