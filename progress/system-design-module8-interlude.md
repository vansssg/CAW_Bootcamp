# System Design Knight Capital interlude (M8 → M9)

## 1. Same version on every server

The loss was mixed versions plus a reused feature flag, not a bad compile. This repo tags images `url-shortener:${{ github.sha }}`. Deploy waits on `/ready` (not `/live`) when `DEPLOY_BASE_URL` is set. Mixed-version window: old and new processes both serving `/r` and `/links/search` until the last replica rolls. Mitigation we already named in Production M08: do not call the deploy done on `/live` 200; require `/ready` plus a smoke POST `/links` + GET `/r`. This laptop cannot prove a live roll — Docker engine is down — so that remains a gate, not a timed rollback.

`image_sha` on `/ready` is the check that Knight lacked: if one replica reports a different SHA, it is the eighth server.

## 2. Seconds, not 45 minutes

`/live` staying 200 is the wrong signal (Debugging M06: live 200 in 0.003s during retries). “This is not normal” here: search `page_size` rejected rate, `cache_sot_mismatch` count, create 5xx, or `/ready` 503. A kill switch analogue is stop serving writes (`POST /links`) while redirects stay up — not “wait for someone to notice empty first pages.”

Power Peg analogue: a feature flag that re-enables a test path (debug error, un-capped `limit`) in production. Do not reuse flags.
