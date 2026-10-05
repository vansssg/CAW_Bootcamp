# System Design Module 09 REFLECT

## Testing strategy

**A `unit_heavy`.** Expensive failures (401, IDOR 404, `javascript:` 400, `GET /r` 307) live in-process. Postgres/Redis/Docker are down. Tests use the real FastAPI app over ASGI, not MagicMock cache.

The callback is real: isolation was incomplete. We did not mock the DB and then miss SQL — we leaked the `links` OrderedDict. Full suite `4 != 0`; solo OK. That is shared process state, the unit-heavy failure mode.

## One rule to enforce

Every test `setUp` must reset `links`, jobs, cache, and rate limits. Never point a suite at `DATABASE_URL` from `.env`.

`progress/state.json` next: Module 10 context.
