# System Design Module 08 CONTEXT

Discovery needs: URL substring, tag filter, sort by created time or click count. Goal is safe/predictable search, not a search engine. Unbounded search has already taken down primaries in the wild; this service already has the seed of that bug.

## 1. Maximum page_size: 50

`GET /api/admin/links` today: default `limit=10`, reject only `limit < 1`. There is **no max**. `MAX_IN_MEMORY_LINKS = 10_000`, so `limit=10000` dumps the whole SoT in one JSON. When Postgres is the miss path, the same unbounded `LIMIT` is a sequential scan during peak — the incident in the lesson.

50 is 5× the current default, enough for an admin page, and small enough that even `ILIKE '%x%'` cannot return the full 10k map. Default stays 10. Values `> 50` → 400, not silent clamp (silent clamp hides client bugs).

Not 1000: that is still a full-table-shaped response on this host. Not “unlimited for admins”: admin is still one process and `/live` does not measure query cost.

## 2. Allowlist: `sort` (and `order`)

Allow only `created_at` | `clicks` and `asc` | `desc`. Never interpolate a query string into `ORDER BY`. Substring `q` is parameterized (`ILIKE` with escaped `%`/`_`, or in-memory `in url`), not concatenated SQL. Tags: equality on a stored list, not a free-form expression language.

Injection we are actually preventing: `sort=clicks; DROP TABLE` or `sort=created_at) ASC, (SELECT ...`.

## Environment (honest)

Postgres `localhost:5432` and Redis `localhost:6379` are not serving. Search BUILD will be owner-scoped in-memory first; we will not claim a live `EXPLAIN` on an index.
