# Knight Capital interlude — applied to this shortener

## 1. Same version on every instance?

This repo’s “pipeline” is `git push origin main`. CI runs ruff + `test_query_columns.py`. It does **not** SSH, does not compare image digests, and does not wait for every replica. Local run is one container named `url-shortener-prod` if Docker is up — there are not eight servers, but the Knight shape is still here: **push success is treated as deploy success**. Nothing in Module 02/overview verifies that every process serving `/r/{code}` is the same git SHA. A missed instance would keep the old `app/main.py` (old `/ready` path, old breaker constants).

## 2. Dead code / repurposed flags

- `/debug/error` is still mounted in the production app. It is Power Peg-adjacent: old drill code that still executes if anyone hits it.
- `/health` still returns `{"ok": true}` with **no** DB check while `/readyz` is the real probe. A flag or LB that still points at `/health` or stale `/ready` would look green or 404 while `/readyz` is 503.
- BREAK this module: `/ready` was renamed to `/readyz`. Same name collision class as Knight’s feature flag — old clients interpret the old path.

## 3. Kill switch for “up but destroying”

Module 07 runbooks cover down/slow/5xx. They do **not** cover “every 307 is sending users to the wrong place after a bad deploy.” Closest stop: `git revert --no-edit HEAD` + `docker stop url-shortener-prod` in the overview. There is no documented “drain traffic / disable redirects” switch. HighErrorRate would fire if those 307s became 5xx; it would **not** fire if redirects succeeded to a malicious URL.

Carry into Module 08: verify the running process’s probe path and git SHA **before** calling the deploy done; have one command that stops taking traffic.
