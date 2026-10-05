# Module 05 BUILD — Iteration log

Strategy: refine-first (A). Structural floor was service-layer pub/sub, not Postgres NOTIFY (5432 not serving).

## Iteration 1
Type: initial
Structural: 4
Surface: 3
Key issues: bus and team isolation were right; invite create did not publish; first WS sketch flushed only when the client sent a message (demo-not-push).
Decision: refine
Reasoning: architecture (service events, team channels, header auth) is sound. Missing publish and push are surface.

## Iteration 2
Type: refinement
Structural: 4
Surface: 4
Key issues: `asyncio.Queue` writer pushes without waiting for client speak; `createInvitation`/`acceptInvitation` publish `invitation.created` / `invitation.accepted` without email in payload.
Decision: refine
Reasoning: scores held or rose. Probe: ITER_INVITE_CREATED_EVENT True, ITER_NO_EMAIL_IN_PAYLOAD True, ITER_ISOLATION_TEAM2_NOT_IN_TEAM1 True.

## Iteration 3
Type: refinement
Structural: 4
Surface: 4
Key issues: `replay_since` and JSON ping/pong. No background 30s heartbeat task (constants only); no httpx so WS handshake not live-tested.
Decision: ship after round 4 polish of log/probe, not a restart
Reasoning: two refinements converged. Restart would rebuild the same bus. Remaining gaps are test-harness (no httpx) and a timer, not a wrong transport.

## Iteration 4
Type: refinement (probe + log)
Structural: 4
Surface: 4
Key issues: none structural. Ship `/ws/teams/{team_id}/activity` with membership close 4403.
Decision: ship
Reasoning: four-iteration budget. Do not spiral into a fake NOTIFY path.

Measured (`python -m app.scripts.module05_activity_probe`):
ITER_BUS_TEAM1_COUNT 1; ITER_ISOLATION_TEAM2_NOT_IN_TEAM1 True; ITER_INVITE_HTTP 200; ITER_INVITE_CREATED_EVENT True; ITER_NO_EMAIL_IN_PAYLOAD True; ITER_ACCEPT_EVENT True; ITER_STRUCTURAL_NOT_NOTIFY True.
