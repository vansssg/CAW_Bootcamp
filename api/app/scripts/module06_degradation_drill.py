import asyncio
import io
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pybreaker

from app.main import app
from app.resilience import db_breaker, retry_with_backoff


async def asgi_request(path: str):
    received = {"status": None}
    body = bytearray()

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            received["status"] = message["status"]
        elif message["type"] == "http.response.body":
            body.extend(message.get("body", b""))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)
    return received["status"], bytes(body)


def test_retry_helper():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ConnectionError("transient blip")
        return "ok"

    result = retry_with_backoff(flaky, max_retries=2, base_delay=0.01, jitter=0.0)
    print("RETRY_HELPER_RESULT", result)
    print("RETRY_HELPER_CALLS", calls["n"])


def test_half_open_close():
    cb = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=1, name="probe")
    def boom():
        raise RuntimeError("down")
    for _ in range(2):
        try:
            cb.call(boom)
        except (RuntimeError, pybreaker.CircuitBreakerError):
            pass
    print("PROBE_STATE_AFTER_FAILS", str(cb.current_state))
    time.sleep(1.05)
    print("PROBE_STATE_AFTER_WAIT", str(cb.current_state))
    print("PROBE_TRIAL", cb.call(lambda: "ok"))
    print("PROBE_STATE_AFTER_SUCCESS", str(cb.current_state))


def main():
    test_retry_helper()
    test_half_open_close()
    db_breaker.close()

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    timings = []
    statuses = []
    try:
        for i in range(10):
            t0 = time.perf_counter()
            status, body = asyncio.run(asgi_request("/ready"))
            elapsed = time.perf_counter() - t0
            timings.append(round(elapsed, 3))
            statuses.append(status)
            print(f"READY_{i}_STATUS", status, "ELAPSED_S", round(elapsed, 3), "BODY", body.decode()[:80])
    finally:
        logger.removeHandler(handler)

    logs = stream.getvalue()
    print("STATUSES", statuses)
    print("TIMINGS", timings)
    print("HAS_CIRCUIT_OPENED_LOG", "circuit_state_change" in logs and "open" in logs.lower())
    print("HAS_CIRCUIT_OPEN_FALLBACK", "circuit_open_fallback" in logs)
    print("HAS_TIMEOUT_LOG", "database unavailable" in logs or "timeout" in logs.lower())
    fast = [t for t in timings[5:] if t < 0.2]
    print("FAST_AFTER_THRESHOLD_COUNT", len(fast))
    print("FAST_AFTER_THRESHOLD_SAMPLE", timings[5:])
    print("DB_RESTART_SKIPPED", "Postgres is not running locally; half-open close proven via probe breaker, not docker start")


if __name__ == "__main__":
    main()
