import asyncio
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B, NOT_OWNER_STATUS
from app.main import app, links
from app.ratelimit import (
    ANALYTICS_PER_MIN,
    CREATE_LINK_PER_MIN,
    REDIRECT_PER_MIN,
    reset_for_tests,
)


async def asgi_request(method: str, path: str, body: bytes = b"", headers=None, query=b""):
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
        "query_string": query,
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


def json_body(result):
    return json.loads(result[2].decode("utf-8"))


def main():
    reset_for_tests()
    links.clear()

    no_auth = run("POST", "/links", body=b'{"long_url":"https://example.com"}')
    print("NO_AUTH_CREATE_STATUS", no_auth[0])
    print("NO_AUTH_CREATE_BODY", no_auth[2].decode("utf-8")[:200])

    bad_key = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com"}',
        headers={"X-API-Key": "wrong-key"},
    )
    print("BAD_KEY_CREATE_STATUS", bad_key[0])

    live = run("GET", "/live")
    print("PUBLIC_LIVE_STATUS", live[0])

    created_a = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/a"}',
        headers={"X-API-Key": API_KEY_A},
    )
    print("CREATE_A_STATUS", created_a[0])
    payload_a = json_body(created_a)
    print("CREATE_A_BODY", json.dumps(payload_a))
    code_a = payload_a["short_code"]

    created_b = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/b"}',
        headers={"X-API-Key": API_KEY_B},
    )
    payload_b = json_body(created_b)
    code_b = payload_b["short_code"]
    print("CREATE_B_STATUS", created_b[0], "CODE", code_b, "OWNER", payload_b.get("owner"))

    get_a_as_a = run("GET", f"/links/{code_a}", headers={"X-API-Key": API_KEY_A})
    print("GET_A_AS_A_STATUS", get_a_as_a[0], get_a_as_a[2].decode("utf-8")[:200])

    get_a_as_b = run("GET", f"/links/{code_a}", headers={"X-API-Key": API_KEY_B})
    print("GET_A_AS_B_STATUS", get_a_as_b[0], get_a_as_b[2].decode("utf-8")[:200])
    print("NOT_OWNER_STATUS_DECISION", NOT_OWNER_STATUS)

    analytics_b_on_a = run(
        "GET",
        f"/links/{code_a}/analytics",
        headers={"X-API-Key": API_KEY_B},
    )
    print("ANALYTICS_A_AS_B_STATUS", analytics_b_on_a[0], analytics_b_on_a[2].decode("utf-8")[:200])

    delete_a_as_b = run("DELETE", f"/links/{code_a}", headers={"X-API-Key": API_KEY_B})
    print("DELETE_A_AS_B_STATUS", delete_a_as_b[0])

    still_there = run("GET", f"/links/{code_a}", headers={"X-API-Key": API_KEY_A})
    print("A_STILL_OWNS_STATUS", still_there[0])

    redir = run("GET", f"/r/{code_a}")
    print("REDIRECT_PUBLIC_STATUS", redir[0], "LOCATION", redir[1].get("location"))

    analytics_a = run("GET", f"/links/{code_a}/analytics", headers={"X-API-Key": API_KEY_A})
    print("ANALYTICS_A_AS_A_STATUS", analytics_a[0], analytics_a[2].decode("utf-8")[:200])

    reset_for_tests()
    create_codes = []
    for i in range(CREATE_LINK_PER_MIN + 2):
        result = run(
            "POST",
            "/links",
            body=b'{"long_url":"https://example.com/rate"}',
            headers={"X-API-Key": API_KEY_A},
        )
        create_codes.append(result[0])
    print("CREATE_RATE_STATUSES", create_codes)
    print("CREATE_RATE_COUNTS", dict(Counter(create_codes)))
    print("CREATE_LINK_PER_MIN", CREATE_LINK_PER_MIN)

    reset_for_tests()
    redirect_codes = []
    for i in range(REDIRECT_PER_MIN + 2):
        result = run("GET", f"/r/{code_a}")
        redirect_codes.append(result[0])
    print("REDIRECT_RATE_STATUSES", redirect_codes)
    print("REDIRECT_RATE_COUNTS", dict(Counter(redirect_codes)))
    print("REDIRECT_PER_MIN", REDIRECT_PER_MIN)

    reset_for_tests()
    analytics_codes = []
    for i in range(ANALYTICS_PER_MIN + 2):
        result = run("GET", f"/links/{code_a}/analytics", headers={"X-API-Key": API_KEY_A})
        analytics_codes.append(result[0])
    print("ANALYTICS_RATE_STATUSES", analytics_codes)
    print("ANALYTICS_RATE_COUNTS", dict(Counter(analytics_codes)))
    print("ANALYTICS_PER_MIN", ANALYTICS_PER_MIN)

    print("RATE_LIMIT_MATRIX", {
        "login_per_min": None,
        "create_link_per_min": CREATE_LINK_PER_MIN,
        "redirect_per_min": REDIRECT_PER_MIN,
        "analytics_per_min": ANALYTICS_PER_MIN,
    })


if __name__ == "__main__":
    main()
