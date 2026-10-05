"""Module 09 unit-heavy suite. Isolated in-memory store; never opens DATABASE_URL."""

import asyncio
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B, NOT_OWNER_STATUS
from app.jobs import RETENTION_DAYS, insert_event_for_tests, purge_old, reset_for_tests as reset_jobs
from app.main import app, links
from app.ratelimit import reset_for_tests as reset_rates
from app.cache import reset_for_tests as reset_cache


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
        header_list.append((key.lower().encode("latin-1"), str(value).encode("latin-1")))
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


def call(method, path, **kwargs):
    return asyncio.run(asgi_request(method, path, **kwargs))


class IsolatedAppTests(unittest.TestCase):
    def setUp(self):
        reset_rates()
        reset_jobs()
        reset_cache()
        links.clear()

    def _create(self, key, url="https://www.example.com/ok"):
        status, _, body = call(
            "POST",
            "/links",
            body=json.dumps({"long_url": url}).encode(),
            headers={"X-API-Key": key},
        )
        data = json.loads(body.decode() or "{}")
        return status, data

    def test_create_link(self):
        status, data = self._create(API_KEY_A)
        self.assertEqual(status, 200)
        self.assertEqual(data.get("persisted"), "memory")
        self.assertIn(data.get("short_code"), links)

    def test_redirect_prefix_r(self):
        _, data = self._create(API_KEY_A, "https://www.example.com/dest")
        code = data["short_code"]
        status, headers, _ = call("GET", f"/r/{code}")
        self.assertEqual(status, 307)
        self.assertEqual(headers.get("location"), "https://www.example.com/dest")

    def test_auth_protected_401(self):
        status, _, _ = call("GET", "/links/search")
        self.assertEqual(status, 401)

    def test_idor_owner_scope(self):
        _, created = self._create(API_KEY_A)
        code = created["short_code"]
        get_b, _, _ = call("GET", f"/links/{code}", headers={"X-API-Key": API_KEY_B})
        patch_b, _, _ = call(
            "PATCH",
            f"/links/{code}",
            body=json.dumps({"long_url": "https://evil.example/x"}).encode(),
            headers={"X-API-Key": API_KEY_B},
        )
        del_b, _, _ = call("DELETE", f"/links/{code}", headers={"X-API-Key": API_KEY_B})
        self.assertEqual(get_b, NOT_OWNER_STATUS)
        self.assertEqual(patch_b, NOT_OWNER_STATUS)
        self.assertEqual(del_b, NOT_OWNER_STATUS)
        self.assertIn(code, links)

    def test_retention_purge(self):
        _, created = self._create(API_KEY_A)
        code = created["short_code"]
        old = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS + 10)).isoformat().replace("+00:00", "Z")
        fresh = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        insert_event_for_tests({"short_code": code, "ts": old, "job_id": "old"})
        insert_event_for_tests({"short_code": code, "ts": fresh, "job_id": "fresh"})
        removed = purge_old()
        self.assertEqual(removed, 1)
        status, _, body = call(
            "GET",
            f"/links/{code}/analytics",
            headers={"X-API-Key": API_KEY_A},
        )
        data = json.loads(body.decode() or "{}")
        self.assertEqual(status, 200)
        self.assertEqual(data.get("clicks"), 1)
        self.assertEqual(data.get("retention_days"), RETENTION_DAYS)

    def test_url_validation_rejects_javascript(self):
        status, _data = self._create(API_KEY_A, "javascript:alert(1)")
        self.assertEqual(status, 400)
        self.assertEqual(len(links), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
