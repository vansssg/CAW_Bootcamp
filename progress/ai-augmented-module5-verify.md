# AI-Augmented Engineering Module 05 VERIFY

## Trajectory

| Round | Structural | Surface | Trajectory |
|-------|------------|---------|------------|
| 1 | 4 | 3 | baseline (bus + team channels; no invite publish) |
| 2 | 4 | 4 | up (Queue push + invitation events) |
| 3 | 4 | 4 | flat-high (replay + ping) |
| 4 | 4 | 4 | ship |

Highest quality: rounds 2–4 (last equals best). No restart. Refine-first served this task: structure was already pub/sub.

## Functional (ASGI websocket, no httpx)

`python -m app.scripts.module05_activity_verify`

1. Connection: `VERIFY_WS_ACCEPT True` (principal-a, team 1 member)
2. Event delivery: `VERIFY_WS_GOT_INVITE_EVENT True` after `publish(1, invitation.created)`
3. Disconnect: `VERIFY_SUBSCRIBER_CLEANUP True` (`_subscribers[1]` empty)
4. Reconnect: `VERIFY_RECONNECT_GOT_MISSED True` (replay since first ts delivered invitation_id 2 only)
5. Unauth: `VERIFY_WS_UNAUTH_CLOSE True` (close 4401)

Did not nest `asyncio.run` HTTP inside the WS loop.
