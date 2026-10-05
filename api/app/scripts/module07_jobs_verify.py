import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.jobs import drain_once, hash_ip, insert_event_for_tests, process_job, reset_for_tests, set_queue_down
from app.main import app, links
from app.ratelimit import reset_for_tests as reset_rates
from app.cache import reset_for_tests as reset_cache


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
        "client": ("203.0.113.9", 12345),
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
    reset_cache()
    links.clear()

    created = run(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/jobs"}',
        headers={"X-API-Key": API_KEY_A},
    )
    code = json.loads(created[2])["short_code"]
    print("CREATE_STATUS", created[0], "CODE", code)

    r1 = run("GET", f"/r/{code}", headers={"User-Agent": "upsk-agent", "Referer": "https://ref.example"})
    r2 = run("GET", f"/r/{code}", headers={"User-Agent": "upsk-agent"})
    print("REDIRECT1", r1[0], r1[1].get("location"))
    print("REDIRECT2", r2[0])
    drain_once()

    q = quote("from=2000-01-01&to=2100-01-01", safe="=&")
    analytics = run(
        "GET",
        f"/links/{code}/analytics",
        headers={"X-API-Key": API_KEY_A},
        query=b"from=2000-01-01&to=2100-01-01",
    )
    body = json.loads(analytics[2])
    print("ANALYTICS_STATUS", analytics[0], "BODY", json.dumps(body))
    print("CLICKS_AFTER_TWO_REDIRECTS", body.get("clicks"))
    print("STORES_RAW_IP", body.get("stores_raw_ip"))
    print("IP_HASH_SAMPLE", body.get("ip_hash_sample"))
    print("EXPECTED_IP_HASH", hash_ip("203.0.113.9"))
    print("RAW_IP_IN_BODY", "203.0.113.9" in analytics[2].decode())

    job = {
        "job_id": "replay-same-id",
        "short_code": code,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "user_agent": "replay",
        "referrer": "",
        "ip_hash": hash_ip("203.0.113.9"),
    }
    print("IDEM_FIRST", process_job(job))
    print("IDEM_SECOND", process_job(job))
    analytics2 = run(
        "GET",
        f"/links/{code}/analytics",
        headers={"X-API-Key": API_KEY_A},
        query=b"from=2000-01-01&to=2100-01-01",
    )
    print("CLICKS_AFTER_REPLAY", json.loads(analytics2[2]).get("clicks"))

    set_queue_down(True)
    r3 = run("GET", f"/r/{code}")
    print("QUEUE_DOWN_REDIRECT", r3[0], r3[1].get("location"))
    set_queue_down(False)

    old_ts = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat().replace("+00:00", "Z")
    insert_event_for_tests(
        {
            "job_id": "old-click",
            "short_code": code,
            "ts": old_ts,
            "user_agent": "old",
            "referrer": "",
            "ip_hash": hash_ip("203.0.113.9"),
        }
    )
    before = json.loads(
        run("GET", f"/links/{code}/analytics", headers={"X-API-Key": API_KEY_A}, query=b"from=2000-01-01&to=2100-01-01")[2]
    )
    purged = run("POST", "/api/admin/purge-clicks", headers={"X-API-Key": API_KEY_A})
    after = json.loads(
        run("GET", f"/links/{code}/analytics", headers={"X-API-Key": API_KEY_A}, query=b"from=2000-01-01&to=2100-01-01")[2]
    )
    print("PURGE_STATUS", purged[0], purged[2].decode()[:200])
    print("CLICKS_BEFORE_PURGE", before.get("clicks"), "AFTER", after.get("clicks"))


if __name__ == "__main__":
    main()
