# System Design Module 08 DECIDE

Choice: **A** (`decisions.module_08.search_strategy = db_native`)

Module 02 already chose PostgreSQL. Admin discovery here is substring + tags + sort, not typo-tolerant product search. After `POST /links` the owner must see the row on the next `GET` — index lag (eventual consistency) is not acceptable for 10k owner-scoped links. Elasticsearch/Meilisearch is another cluster; Docker engine and Redis are already down on this host, so we would be designing a search engine we cannot run.

Tradeoff: no fuzzy matching; `ILIKE '%q%'` can still sequential-scan. Mitigation from CONTEXT: `page_size` max 50, parameterized `q`, allowlisted `sort`. In-memory filter while 5432 is down is the same contract, not a fake ES cluster.
