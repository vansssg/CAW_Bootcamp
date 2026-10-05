# System Design Module 04 BREAK

Injected (hard / adaptive): **IDOR** on `GET /api/admin/links` — the handler authenticates principal-b but returns every in-memory link, including principal-a's `original_url`.

Symptom (ASGI, `module04_auth_break.py`):

- A creates `https://secret.example/a-private` → short_code `c549dcfa`
- B lists admin links with `X-API-Key: API_KEY_B` → **200** body contains `c549dcfa` and the secret URL
- `BREAK_IDOR_LEAK True`

Get-by-id still 404 for non-owners (from BUILD verify). The list path skipped the owner filter, which is the same class of bug as changing the id on a hotel key card.

Root cause (for FIX): `list_links` iterates `links.items()` without `if rec.get("owner") == principal_id`.
