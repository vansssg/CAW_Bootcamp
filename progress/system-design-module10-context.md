# System Design Module 10 CONTEXT

Shipping is ports, env, `/live` vs `/ready`, shutdown, migrations, repeatable builds. This image already encodes the two micro-exercise answers.

## 1. Bind to localhost on Railway

Railway’s proxy connects to the container’s **published port on the container network**, not to the process’s loopback. `uvicorn --host 127.0.0.1` only accepts connections from inside the container. The platform’s health checks and public URL get connection refused / timeout. The app looks “up” in logs and still fails the deploy.

This Dockerfile uses `--host 0.0.0.0` so the listener is on all interfaces. HEALTHCHECK uses `127.0.0.1` **on purpose** — that probe runs *inside* the container.

## 2. Hardcode the port when the platform sets PORT

Railway injects `PORT`. If CMD is `--port 3000` and the platform routes to `PORT=8080`, the proxy talks to an empty port. `EXPOSE 3000` does not change that. CMD here is `--port ${PORT:-3000}`. Config still validates `PORT` 1–65535 from env (`api/app/config.py`).

## Honest bound

`/live` is `{ok:true}` with no DB. `/ready` is 503 while `localhost:5432` times out. Docker engine is down — we will not claim a Railway deploy succeeded.
