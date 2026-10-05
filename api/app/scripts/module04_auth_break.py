import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.main import app, links
from app.ratelimit import reset_for_tests


async def asgi_request(method: str, path: str, body: bytes = b"", headers=None):
    received = {"status": None}
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
    return received["status"], bytes(out)


def run(method, path, **kwargs):
    return asyncio.run(asgi_request(method, path, **kwargs))


def main():
    reset_for_tests()
    links.clear()

    created = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://secret.example/a-private"}',
        headers={"X-API-Key": API_KEY_A},
    )
    payload = json.loads(created[1].decode("utf-8"))
    code_a = payload["short_code"]
    print("BREAK_CREATE_A_STATUS", created[0], "CODE", code_a)

    listed = run("GET", "/api/admin/links", headers={"X-API-Key": API_KEY_B})
    body = listed[1].decode("utf-8")
    print("BREAK_LIST_B_STATUS", listed[0])
    print("BREAK_LIST_B_BODY", body)
    leaked = code_a in body and "https://secret.example/a-private" in body
    print("FIX_LIST_B_STATUS", listed[0])
    print("FIX_LIST_B_BODY", body)
    print("FIX_IDOR_LEAK", leaked)
    print("FIX_CLASS", "owner-scoped admin list")

    jwt_as_key = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/jwt-alias"}',
        headers={"X-API-Key": "development-only-secret-minimum-32-characters"},
    )
    print("FIX_JWT_SECRET_AS_API_KEY_STATUS", jwt_as_key[0], jwt_as_key[1].decode("utf-8")[:120])


if __name__ == "__main__":
    main()
