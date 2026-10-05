"""BREAK: delete + recreate same short_code doubles analytics if events are not purged."""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.cache import namespace_keys, reset_for_tests as reset_cache
from app.jobs import drain_once, events_for, reset_for_tests as reset_jobs
from app.main import URLS_TOTAL, links
from app.ratelimit import reset_for_tests as reset_rates
from app.scripts.module05_failure_fix_verify import asgi_request

CODE = "deadbeef"


def seed():
    links[CODE] = {
        "long_url": "https://example.com/reused",
        "owner": "principal-a",
        "clicks": 0,
    }
    URLS_TOTAL.set(len(links))


async def clicks():
    drain_once()
    return len(events_for(CODE, None, None))


async def main():
    reset_cache()
    reset_rates()
    reset_jobs()
    links.clear()
    seed()
    await asgi_request("GET", f"/r/{CODE}")
    await asgi_request("GET", f"/r/{CODE}")
    before_delete = await clicks()
    deleted = await asgi_request("DELETE", f"/links/{CODE}", headers={"X-API-Key": API_KEY_A})
    after_delete_events = await clicks()
    seed()
    await asgi_request("GET", f"/r/{CODE}")
    await asgi_request("GET", f"/r/{CODE}")
    after_recreate = await clicks()
    print("BEFORE_DELETE_CLICKS", before_delete)
    print("DELETE_STATUS", deleted[0])
    print("AFTER_DELETE_EVENTS", after_delete_events)
    print("AFTER_RECREATE_CLICKS", after_recreate)
    print("DOUBLED", after_recreate == before_delete * 2)
    ns = namespace_keys()
    print("REDIRECT_KEYS", ns["redirect"])
    print("DEDUP_KEYS_PREFIX_OK", all(k.startswith("analytics:dedup:") for k in ns["dedup"]))
    print("REDIRECT_PREFIX_OK", all(k.startswith("link:redirect:") for k in ns["redirect"]))
    print("NAMESPACES_DISJOINT", not set(ns["redirect"]) & set(ns["dedup"]))


if __name__ == "__main__":
    asyncio.run(main())
