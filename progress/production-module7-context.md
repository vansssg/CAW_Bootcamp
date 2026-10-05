# Production Module 07 CONTEXT — 3 AM you vs a runbook

At 3 AM you are not 2 PM you. A runbook is a letter from caffeinated-you: exact commands, not “restart the service.” The 2:47 AM pool-exhaustion page became `docker rm myservice-prod` instead of `docker restart myservice-prod` — five characters, lost volume data.

## Micro-exercise 1 — from memory (then checked)

From memory before opening files:

- Env: `DATABASE_URL`, `JWT_SECRET`, `APP_ENV`, `PORT`, `API_KEY_A`, `API_KEY_B`, `REDIS_URL`, `LOG_LEVEL`, `CORS_ORIGIN`
- Deps: Postgres `localhost:5432`, Redis `localhost:6379` (both often down here), in-process cache/queue fallbacks

Later confirmed against `api/.env.example` — the memory list matched. Gap a runbook closes: I would not have been sure about `CORS_ORIGIN` at 3 AM.

## Micro-exercise 2 — first three commands for “service is slow”

Exact, not descriptions. Never `docker rm`.

```bash
curl -sS -m 2 -o /dev/null -w "%{http_code} time=%{time_total}\n" http://127.0.0.1:8000/live
curl -sS -m 3 -o /dev/null -w "%{http_code} time=%{time_total}\n" http://127.0.0.1:8000/ready
curl -sS -m 2 http://127.0.0.1:8000/metrics | findstr /i "http_request duration"
```

If `/live` is fast 200 and `/ready` is ~4s 503, do **not** hammer `/ready` (M06 breaker half-open). Check logs for `circuit_open_fallback`. This workspace has no running `myservice-prod` container — do not type `docker rm`.
