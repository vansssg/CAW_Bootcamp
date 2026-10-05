import asyncio
import io
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.main import app

SENTINEL = "DO_NOT_LOG_ME_123"


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


def run(method, path, **kwargs):
    return asyncio.run(asgi_request(method, path, **kwargs))


def main():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger("app").addHandler(handler)

    validation = run(
        "POST",
        "/links",
        body=b'{"long_url":"not-a-url"}',
        headers={"X-API-Key": API_KEY_A},
    )
    print("VALIDATION_STATUS", validation[0])
    print("VALIDATION_BODY", validation[2].decode("utf-8")[:400])
    print("VALIDATION_HAS_TRACE", "Traceback" in validation[2].decode("utf-8"))
    print("VALIDATION_X_REQUEST_ID", validation[1].get("x-request-id"))

    schema = run(
        "POST",
        "/links",
        body=b'{"long_url":123}',
        headers={"X-API-Key": API_KEY_A},
    )
    print("SCHEMA_STATUS", schema[0])
    print("SCHEMA_BODY", schema[2].decode("utf-8")[:400])

    server = run("GET", "/debug/error")
    print("SERVER_STATUS", server[0])
    print("SERVER_BODY", server[2].decode("utf-8")[:400])
    print("SERVER_HAS_TRACE", "Traceback" in server[2].decode("utf-8") or "RuntimeError" in server[2].decode("utf-8"))
    print("SERVER_X_REQUEST_ID", server[1].get("x-request-id"))

    sentinel = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com"}',
        headers={"X-API-Key": SENTINEL},
    )
    print("SENTINEL_STATUS", sentinel[0])
    print("SENTINEL_BODY", sentinel[2].decode("utf-8")[:300])
    logs = stream.getvalue()
    print("SENTINEL_IN_LOGS", SENTINEL in logs)
    print("LOG_HAS_REQUEST_ID", "request_id=" in logs)
    print("LOG_HAS_STACK_FOR_500", "stack_trace=" in logs or "Traceback" in logs)


if __name__ == "__main__":
    main()
