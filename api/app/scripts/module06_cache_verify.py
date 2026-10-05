import asyncio
import io
import json
import logging
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.cache import redis_is_down, reset_for_tests
from app.main import app, links
from app.ratelimit import REDIRECT_PER_MIN, reset_for_tests as reset_rates


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
    reset_for_tests()
    reset_rates()
    links.clear()
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger("app").addHandler(handler)

    print("REDIS_DOWN", redis_is_down())

    created = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/cached"}',
        headers={"X-API-Key": API_KEY_A},
    )
    payload = json.loads(created[2].decode())
    code = payload["short_code"]
    print("CREATE_STATUS", created[0], "CODE", code)

    first = run("GET", f"/r/{code}")
    print("FIRST_REDIRECT_STATUS", first[0], "LOCATION", first[1].get("location"))
    second = run("GET", f"/r/{code}")
    print("SECOND_REDIRECT_STATUS", second[0], "LOCATION", second[1].get("location"))

    patched = run(
        "PATCH",
        f"/links/{code}",
        body=b'{"long_url":"https://example.org/new"}',
        headers={"X-API-Key": API_KEY_A},
    )
    print("PATCH_STATUS", patched[0], patched[2].decode()[:200])
    third = run("GET", f"/r/{code}")
    print("POST_PATCH_REDIRECT_STATUS", third[0], "LOCATION", third[1].get("location"))
    print("STALE_AVOIDED", third[1].get("location") == "https://example.org/new")

    reset_rates()
    statuses = []
    for _ in range(REDIRECT_PER_MIN + 2):
        statuses.append(run("GET", f"/r/{code}")[0])
    print("ABUSE_REDIRECT_STATUSES", statuses)
    print("ABUSE_REDIRECT_COUNTS", dict(Counter(statuses)))

    logs = stream.getvalue()
    print("LOG_CACHE_MISS", "cache_miss" in logs)
    print("LOG_CACHE_HIT", "cache_hit" in logs)
    print("LOG_CACHE_SET", "cache_set" in logs)
    print("LOG_CACHE_INVALIDATE", "cache_invalidate" in logs)
    print("LOG_REDIS_DOWN_FALLBACK", "cache_redis_down_fallback" in logs)


if __name__ == "__main__":
    main()
