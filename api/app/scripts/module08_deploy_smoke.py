"""Module 08 local smoke: probes + business create/redirect (ASGI, no Docker)."""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.main import IMAGE_SHA, MAX_IN_MEMORY_LINKS
from app.scripts.module05_failure_fix_verify import asgi_request


async def run():
    live = await asgi_request("GET", "/live")
    ready = await asgi_request("GET", "/ready")
    metrics = await asgi_request("GET", "/metrics")
    create = await asgi_request(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/module08-smoke"}',
        headers={"X-API-Key": API_KEY_A},
    )
    created = json.loads(create[2].decode()) if create[2] else {}
    code = created.get("short_code")
    redir = await asgi_request("GET", f"/r/{code}") if code else (None, {}, b"")
    debug = await asgi_request("GET", "/debug/error")
    ready_body = ready[2].decode()
    metrics_body = metrics[2].decode()
    print("LIVE", live[0], live[2].decode()[:80])
    print("READY", ready[0], ready_body[:240])
    print("METRICS", metrics[0], "http_requests_total", "http_requests_total" in metrics_body)
    print("POST_LINKS", create[0], "persisted", created.get("persisted"))
    print("REDIRECT", redir[0])
    print("DEBUG_ERROR", debug[0], "APP_ENV_NOT_PRODUCTION_STILL_500_OK")
    print("IMAGE_SHA", IMAGE_SHA)
    print("MAX_IN_MEMORY_LINKS", MAX_IN_MEMORY_LINKS)
    print("READY_HAS_IMAGE_SHA", "image_sha" in ready_body)
    ok = (
        live[0] == 200
        and ready[0] == 503
        and metrics[0] == 200
        and create[0] == 200
        and redir[0] == 307
        and "image_sha" in ready_body
    )
    print("SMOKE_OK", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
