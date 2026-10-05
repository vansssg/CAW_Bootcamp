import asyncio
import io
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import DB_CONNECT_TIMEOUT_S, engine
from app.main import app


async def asgi_request(method: str, path: str, body: bytes = b"", headers=None):
    received = {"status": None, "headers": []}
    out = bytearray()
    sent = {"done": False}

    async def receive():
        if not sent["done"]:
            sent["done"] = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            received["status"] = message["status"]
            received["headers"] = message.get("headers", [])
        elif message["type"] == "http.response.body":
            out.extend(message.get("body", b""))

    header_list = []
    for key, value in (headers or {}).items():
        header_list.append((key.lower().encode("latin-1"), value.encode("latin-1")))
    if body and not any(k == b"content-type" for k, _ in header_list):
        header_list.append((b"content-type", b"application/json"))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": header_list,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)
    header_map = {
        k.decode("latin-1").lower(): v.decode("latin-1") for k, v in received["headers"]
    }
    return received["status"], header_map, bytes(out)


def timed(label, coro):
    t0 = time.perf_counter()
    result = asyncio.run(coro)
    elapsed = time.perf_counter() - t0
    print(f"{label}_STATUS", result[0])
    print(f"{label}_ELAPSED_S", round(elapsed, 3))
    print(f"{label}_BODY", result[2].decode("utf-8", errors="replace")[:200])
    return elapsed, result


def main():
    print("ENGINE_CONNECT_TIMEOUT_S", DB_CONNECT_TIMEOUT_S)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        live_elapsed, live = timed("FIX_LIVE", asgi_request("GET", "/live"))
        ready_elapsed, ready = timed("FIX_READY", asgi_request("GET", "/ready"))
        payload = json.dumps({"long_url": "https://example.com/fix"}).encode()
        create_elapsed, created = timed(
            "FIX_CREATE",
            asgi_request("POST", "/links", body=payload),
        )
        redir_elapsed, redir = timed("FIX_REDIRECT", asgi_request("GET", "/r/abc123"))
    finally:
        logger.removeHandler(handler)

    logs = stream.getvalue()
    print("FIX_LIVE_OK", live[0] == 200)
    print("FIX_READY_IS_503", ready[0] == 503)
    print("FIX_CREATE_IS_503", created[0] == 503)
    print("FIX_REDIRECT_IS_503", redir[0] == 503)
    print("FIX_READY_UNDER_15S", ready_elapsed < 15)
    print("FIX_CREATE_UNDER_15S", create_elapsed < 15)
    print("FIX_NO_STACK_TO_USER", "Traceback" not in created[2].decode("utf-8", errors="replace"))
    print("FIX_USER_DETAIL", "temporarily unavailable" in created[2].decode("utf-8", errors="replace"))
    print("FIX_LOG_HAS_DB_UNAVAILABLE", "database unavailable" in logs)
    print("FIX_LOG_HAS_FAILURE_MODE", "postgres_connect_or_query_timeout" in logs)
    print("FIX_LOG_HAS_READY_ACTION", "action=ready" in logs or '"action": "ready"' in logs)


if __name__ == "__main__":
    main()
