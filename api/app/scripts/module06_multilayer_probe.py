"""Module 06 BUILD: stale-cache SoT check + retry storm vs bulkhead worker."""
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.cache import get_redirect_target, set_redirect_target
from app.db import API_POOL_SIZE, WORKER_POOL_SIZE, engine, worker_engine
from app.jobs import (
    JOB_RETRY_MAX,
    dead_letters,
    process_job_with_retry,
    reset_for_tests,
    retry_delays_s,
    set_persist_for_tests,
)
from app.main import links
from app.scripts.module05_failure_fix_verify import asgi_request


async def main():
    print("POOL_ISOLATED", engine.pool is not worker_engine.pool)
    print("API_POOL_SIZE", API_POOL_SIZE, "WORKER_POOL_SIZE", WORKER_POOL_SIZE)
    print("RETRY_DELAYS_S", retry_delays_s())

    created = await asgi_request(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/bug9-sot"}',
        headers={"X-API-Key": API_KEY_A},
    )
    code = json.loads(created[2].decode())["short_code"]
    r1 = await asgi_request("GET", f"/r/{code}")
    print("WARM_REDIRECT", r1[0], r1[1].get("location"))

    deleted = await asgi_request("DELETE", f"/links/{code}", headers={"X-API-Key": API_KEY_A})
    print("DELETE_STATUS", deleted[0], "SOT", code in links)
    r2 = await asgi_request("GET", f"/r/{code}")
    print("AFTER_DELETE_REDIRECT", r2[0], r2[2].decode()[:80])

    created2 = await asgi_request(
        "POST",
        "/links",
        body=b'{"long_url":"https://example.com/stale-seed"}',
        headers={"X-API-Key": API_KEY_A},
    )
    code2 = json.loads(created2[2].decode())["short_code"]
    await asgi_request("GET", f"/r/{code2}")
    links.pop(code2, None)
    set_redirect_target(code2, "https://example.com/stale-seed")
    print("SEEDED_STALE_CACHE", bool(get_redirect_target(code2)), "sot", code2 in links)
    r3 = await asgi_request("GET", f"/r/{code2}")
    print("STALE_CACHE_REDIRECT", r3[0], r3[2].decode()[:120])
    print("CACHE_AFTER_SOT_GUARD", bool(get_redirect_target(code2)))

    calls = {"n": 0}

    def boom(_job):
        calls["n"] += 1
        raise RuntimeError("forced_job_fail")

    t_naive = time.perf_counter()
    for _ in range(JOB_RETRY_MAX + 1):
        try:
            boom(None)
        except RuntimeError:
            pass
    naive_s = round(time.perf_counter() - t_naive, 4)
    print("NAIVE_IMMEDIATE_ATTEMPTS", JOB_RETRY_MAX + 1, "elapsed_s", naive_s)

    reset_for_tests()
    calls["n"] = 0
    set_persist_for_tests(boom)
    t0 = time.perf_counter()
    result = process_job_with_retry(
        {
            "job_id": "storm-1",
            "short_code": "dead",
            "ts": "2026-08-17T00:00:00Z",
            "user_agent": "",
            "referrer": "",
            "ip_hash": "x",
        }
    )
    elapsed = round(time.perf_counter() - t0, 3)
    dlq = dead_letters()
    print("RETRY_RESULT", result, "attempts", calls["n"], "elapsed_s", elapsed)
    print("DLQ_LEN", len(dlq), "dlq_attempts", dlq[-1]["attempts"] if dlq else None, "delays_s", dlq[-1]["delays_s"] if dlq else None)

    t1 = time.perf_counter()
    live = await asgi_request("GET", "/live")
    print("LIVE_AFTER_STORM", live[0], "elapsed_s", round(time.perf_counter() - t1, 3))


if __name__ == "__main__":
    asyncio.run(main())
