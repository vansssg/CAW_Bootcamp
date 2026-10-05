# System Design Module 10 REFLECT

## Deployment strategy + why

**A `single_container`.** One image `url-shortener:$SHA` is the rollback unit. HTTP, in-process click worker, `/live`, and `/ready` share that process. We did not deploy a worker+Redis+DB mesh: Docker `info` exit 1, 5432/6379 not serving, no Railway token.

## Operational lesson

Liveness must be `/live` (process up). Readiness must be `/ready` (DB). Pointing the platform check at `/ready` made PROBE 503 while LIVE was 200 — the single container would restart, taking redirects with it. CI still lists `READY=200` for a public URL we do not have; that job was not run.

## Decision callback

Every failure is total: wrong health path, missing PORT, or a SIGKILL without the 30s graceful flag hits API and worker together. Isolation we do have: SQLAlchemy pools, `/live` vs `/ready`. Isolation we do not have: separate processes.

`progress/state.json`: module 10 complete, `bootcamp_complete` true for this skill file. UPSK skill completion still depends on accepted report then `upsk next`.
