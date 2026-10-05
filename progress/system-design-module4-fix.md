# System Design Module 04 FIX

Vulnerability: authentication ≠ authorization. `GET /api/admin/links` required a valid `X-API-Key` (authN) but listed every link in process memory (no owner filter). Principal-b received principal-a's `original_url` (IDOR).

Fixes:
1. Restore `if rec.get("owner") == principal_id` on the admin list (same 404 hide policy as get/delete).
2. Secure config: `API_KEY_A` / `API_KEY_B` are required env vars (≥32 chars, distinct, not equal to `JWT_SECRET`). JWT_SECRET is no longer an API-key alias, so rotating JWT_SECRET cannot leave a second principal-a credential in `API_KEYS`.

Regression (`module04_auth_break.py` after fix):
- FIX_IDOR_LEAK False — B's list is `count:0 items:[]`
- FIX_JWT_SECRET_AS_API_KEY_STATUS 401
- Full matrix still holds in `module04_auth_verify.py`
