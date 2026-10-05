# Production Module 08 REFLECT (capstone)

## Decisions after the drill

Kept **blue-green**. Rolling would have mixed `/ready` and `/readyz` (M07) and mixed memory-SoT vs DB-SoT processes. We never ran two containers (Docker down); the reasoning still holds.

Kept **automated rollback**, but only if it includes the **business smoke**, not `/ready` alone. BREAK: `/ready` 503 on this host while `POST /links` 200 `persisted=memory` and `/r` 307 — the inverse of the prompt, same split. Automated rollback keyed only off `/ready` would **not** fire when `/ready` is 200 and creates are RAM-only. Unexpected: the rollback clock was never started because compose never started.

Would not switch to rolling. Would not switch to purely-manual: this laptop has no pager.

## What “done” means

Not `/ready` 200. Done after: `/live` 200, `/ready` 200 with `database=connected` and `image_sha` matching the git tag, smoke `POST /links` + `GET /r/{code}` 307, `/metrics` has `http_requests_total`. Then watch `urls_total` and `checks.in_memory_links` for **30 minutes** (one TTL window is 60s; 30m catches a climb). Stop the sit-in after 30m if those are flat and HighErrorRate would have had 2m of 5xx — knowing HighErrorRate is not scraped here.

## One Module 01 change

Dockerfile HEALTHCHECK used `/health`, which is the same lie as `/live`. Would have set HEALTHCHECK to `/live` and platform probe to `/ready` on day one so Docker restarts and traffic gating never share a path.

## Hardest / surprise

Hardest: Docker Desktop pipe missing — local fallback deploy is a documented command that cannot run. Surprise: `/ready` 503 and business 200 at the same time; “readiness lies” works in both directions.

## Knowledge check

1. Core problem: upload ≠ deploy; deploy is proven `/ready` + business smoke + SHA, with a rollback you have actually timed.
2. Biggest decision: automated rollback **signal**. `/live` or `/ready` SELECT 1 will not catch RAM SoT. Smoke `POST /links` does.
3. End-to-end: not a public URL. Local proof: SMOKE_OK True — LIVE 200, READY 503 with `image_sha`, POST 200 memory, 307.

Mini VERIFY: `python app/scripts/module08_deploy_smoke.py` → SMOKE_OK True (2026-08-17).

Risk: compose `DATABASE_URL` override without IMAGE_TAG. Mitigation: `/ready` `image_sha` plus gated CI `vars.DEPLOY_BASE_URL`.
