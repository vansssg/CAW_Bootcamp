# System Design Module 09 FIX

Unreliable because `links` is process-global. Without `links.clear()`, `test_url_validation` measured leftover creates (`4 != 0`). Solo it passed.

Fix: restore `links.clear()` in `setUp` with `reset_rates`, `reset_jobs`, `reset_cache`. Isolation is the in-memory store, not a production `DATABASE_URL`.

Determinism: three full runs `OK` (0.690s, 0.849s, 1.461s).
