# System Design Module 06 FIX

Keys: `redir:{code}` in Redis, same code in the in-process TTL map. TTL 60s.
Invalidation: PATCH and DELETE must drop that key. Skipping PATCH invalidation served https://example.com/old after the store had https://example.org/new.

Restored `invalidate_redirect_target(code)` on PATCH. Regression: STALE_AVOIDED True.
