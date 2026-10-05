import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.main import app, links
from app.ratelimit import reset_for_tests as reset_rates
from app.search import SEARCH_PAGE_SIZE_MAX, FTS_SELECT_SQL


async def asgi_request(method: str, path: str, body: bytes = b"", headers=None, query: str = ""):
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
        header_list.append((key.lower().encode("latin-1"), str(value).encode("latin-1")))
    if body and not any(k == b"content-type" for k, _ in header_list):
        header_list.append((b"content-type", b"application/json"))
    q = query.encode("ascii") if isinstance(query, str) else query
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": q,
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


def create(url, key, tags=None):
    payload = {"long_url": url}
    if tags is not None:
        payload["tags"] = tags
    status, _, body = run(
        "POST",
        "/links",
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    data = json.loads(body.decode() or "{}")
    return status, data


def search(key, **params):
    status, _, body = run(
        "GET",
        "/links/search",
        headers={"X-API-Key": key} if key else {},
        query=urlencode(params),
    )
    data = json.loads(body.decode() or "{}")
    return status, data


def main():
    reset_rates()
    links.clear()

    a1 = create("https://www.example.com/alpha", API_KEY_A, ["docs"])
    a2 = create("https://www.example.com/beta", API_KEY_A, ["docs"])
    a3 = create("https://other.example.org/gamma", API_KEY_A, ["news"])
    b1 = create("https://www.example.com/alpha", API_KEY_B, ["docs"])
    print("CREATE_A", a1[0], a2[0], a3[0], "CREATE_B", b1[0])
    print("A_CODES", a1[1].get("short_code"), a2[1].get("short_code"), a3[1].get("short_code"))

    unauth = search(None, q="example", page=1, page_size=10)
    print("UNAUTH_STATUS", unauth[0])

    huge = search(API_KEY_A, q="example", page=1, page_size=SEARCH_PAGE_SIZE_MAX + 1)
    print("HUGE_PAGE_STATUS", huge[0], "DETAIL", huge[1].get("detail") or huge[1].get("error"))

    bad_sort = search(API_KEY_A, q="example", sort="clicks;drop")
    print("BAD_SORT_STATUS", bad_sort[0])

    matched = search(API_KEY_A, q="example", page=1, page_size=10)
    urls = [item["long_url"] for item in matched[1].get("items") or []]
    owners = {item["owner"] for item in matched[1].get("items") or []}
    print("SEARCH_STATUS", matched[0])
    print("SEARCH_TOTAL", matched[1].get("total"))
    print("SEARCH_PAGE", matched[1].get("page"), "PAGE_SIZE", matched[1].get("page_size"))
    print("SEARCH_BACKEND", matched[1].get("backend"))
    print("SEARCH_URLS", urls)
    print("SEARCH_OWNERS", sorted(owners))
    print("B_LEAKED", b1[1].get("short_code") in [item["short_code"] for item in matched[1].get("items") or []])

    tagged = search(API_KEY_A, tag="docs", page=1, page_size=10)
    print("TAG_DOCS_TOTAL", tagged[1].get("total"), "URLS", [i["long_url"] for i in tagged[1].get("items") or []])

    page1 = search(API_KEY_A, q="example", page=1, page_size=1)
    page2 = search(API_KEY_A, q="example", page=2, page_size=1)
    print("P1_COUNT", len(page1[1].get("items") or []), "TOTAL", page1[1].get("total"))
    print("P2_COUNT", len(page2[1].get("items") or []), "TOTAL", page2[1].get("total"))
    print("P1_NE_P2", (page1[1].get("items") or [{}])[0].get("short_code") != (page2[1].get("items") or [{}])[0].get("short_code"))

    page0 = search(API_KEY_A, q="example", page=0, page_size=10)
    print("PAGE0_STATUS", page0[0])

    print("FTS_PARAM_Q", ":q" in FTS_SELECT_SQL and "plainto_tsquery" in FTS_SELECT_SQL)
    print("SEARCH_USE_POSTGRES", __import__("os").getenv("SEARCH_USE_POSTGRES"))


if __name__ == "__main__":
    main()
