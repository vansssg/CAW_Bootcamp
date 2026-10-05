# System Design Module 09 VERIFY

## What does this test protect us from?

The six cases pin the expensive failures from CONTEXT:

- **Create 200** — we can still mint a short code in memory.
- **GET /r 307** — public redirects go to the stored URL (Module 03 `/r/{code}`), not a guessed Location.
- **401 on `/links/search`** — unauthenticated discovery does not list links.
- **IDOR 404** — principal-b cannot GET/PATCH/DELETE principal-a's code (`not_owner_status=404`).
- **Retention** — a 40-day event is purged; analytics `clicks=1`.
- **`javascript:alert(1)` 400** — scheme bypass does not land in `links`.

Together they protect against shipping an auth hole, an open redirect/XSS URL, an IDOR, and inflated click counts.

## How would you know a test is flaky?

It fails sometimes with the same code. Signals here: depending on Redis ping (~0.5s on redirect, `TimeoutError`), leftover `links` or rate-limit buckets across tests, or wall-clock vs `purge_old` without a fixed `now`. We `setUp` with `links.clear()`, `reset_rates()`, `reset_jobs()`, `reset_cache()`. The suite was `Ran 6 tests in 0.605s OK` once; a flake would be a second run that 429s or sees a leftover short code.

## Why is it dangerous if tests hit the real DB?

CONTEXT incident: one wrong `DATABASE_URL` and the suite writes production. `module-02-seed-query.py` already points at `localhost:5432/upsk_sdf`. This suite never opens `DATABASE_URL`; `persisted=memory`. A test INSERT/DELETE against the env URL is the GitLab-style wipe, not a failure.
