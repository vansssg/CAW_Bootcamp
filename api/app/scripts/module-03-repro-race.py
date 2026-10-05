import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = os.getenv("REPRO_BASE_URL", "http://127.0.0.1:3042")
SHORT_CODE = os.getenv("REPRO_SHORT_CODE", "abc123")
CONCURRENCY = int(os.getenv("REPRO_CONCURRENCY", "30"))
ROUNDS = int(os.getenv("REPRO_ROUNDS", "5"))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)


def create_link() -> None:
    payload = json.dumps({"long_url": "https://example.com"}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/links",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        _ = resp.read()


def hit_redirect() -> tuple[int, float, str]:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(f"{BASE_URL}/r/{SHORT_CODE}", method="GET")
        resp = opener.open(req, timeout=5)
        code = resp.getcode()
        _ = resp.read()
        return code, (time.perf_counter() - start) * 1000, ""
    except urllib.error.HTTPError as exc:
        # HTTPError is still a valid HTTP response (e.g., 307/404/500)
        return exc.code, (time.perf_counter() - start) * 1000, str(exc)
    except Exception as exc:
        return -1, (time.perf_counter() - start) * 1000, str(exc)


def run_round(round_idx: int) -> dict:
    results = []
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = [pool.submit(hit_redirect) for _ in range(CONCURRENCY)]
        for future in as_completed(futures):
            results.append(future.result())

    status_counts = {}
    failures = []
    latencies = []
    for code, latency_ms, err in results:
        status_counts[code] = status_counts.get(code, 0) + 1
        latencies.append(latency_ms)
        if code == -1:
            failures.append(err)

    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95) - 1]
    p99 = latencies[int(len(latencies) * 0.99) - 1]

    return {
        "round": round_idx,
        "status_counts": status_counts,
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "failures": failures,
    }


def main() -> None:
    create_link()
    print(f"Repro target: {BASE_URL}/r/{SHORT_CODE}")
    print(f"Concurrency={CONCURRENCY}, Rounds={ROUNDS}")

    saw_500 = False
    for idx in range(1, ROUNDS + 1):
        summary = run_round(idx)
        if 500 in summary["status_counts"]:
            saw_500 = True
        print(json.dumps(summary))

    if saw_500:
        print("BUG REPRODUCED: observed HTTP 500 under concurrent load.")
    else:
        print("NO REPRO: no HTTP 500 observed under current test conditions.")


if __name__ == "__main__":
    main()
