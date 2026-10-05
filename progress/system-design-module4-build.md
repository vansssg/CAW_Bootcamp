# System Design Module 04 BUILD

Auth method: API key (`X-API-Key`), two principals.

- `API_KEY_A` -> `principal-a`
- `API_KEY_B` -> `principal-b`
- `JWT_SECRET` also maps to `principal-a` so the existing operator secret still works as a key value.

not_owner_status: **404** (hide existence; no data leakage to principal B).

Rate limits (`decisions.module_04.rate_limits`):

- login_per_min: n/a (no login route)
- create_link_per_min: 5
- redirect_per_min: 8
- analytics_per_min: 5

Management-plane create/list/get/delete/analytics use the in-memory owner-scoped store. Postgres is not claimed as the write path while `localhost:5432` is down.
