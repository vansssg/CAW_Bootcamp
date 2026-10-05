# System Design Module 04 REFLECT

Chosen auth: **API key** (`X-API-Key` → `principal_id`). Admin is an internal API; revoke is rotation; JWT expiry/invalidation was extra machinery we did not need.

Security practice: authentication ≠ authorization. A valid key on `GET /api/admin/links` still leaked A's URL until the list was owner-scoped. 404-on-not-owner hides existence.

API-key callback: static keys have no expiry. The IDOR was a missing scope check, which a JWT `sub` claim would not have saved either if the list skipped the owner filter. Config fix: keys live in env, must be ≥32 chars, distinct, and not equal to `JWT_SECRET`.

Checkpoint: POST /links without key → 401; with API_KEY_A → 200; GET /r/{code} stays 307 public; 6th create → 429.

Knowledge check:
1. Problem: prove who is calling, then limit what they can see/do, without locking public redirects.
2. Biggest decision: API key + 404 not-owner (hide existence) + per-route rate limits.
3. Evidence: `module04_auth_verify.py` 401/200/404/307/429 matrix; `module04_auth_break.py` IDOR True then False.

Risk: in-memory store and in-process limiter die on restart / do not share across workers. Mitigation: Postgres owner column + Redis limiter when those services are up.

Remaining: Postgres `localhost:5432` still not serving; create/redirect proofs used the in-process owner-scoped store and did not claim a DB write.
