import asyncio
import io
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import HTTP_REQUESTS_TOTAL, app, emit_log


async def asgi_request(method: str, path: str, timeout_s: float = 5.0):
    body = bytearray()
    received = {"status": None}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            received["status"] = message["status"]
        elif message["type"] == "http.response.body":
            body.extend(message.get("body", b""))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    await asyncio.wait_for(app(scope, receive, send), timeout=timeout_s)
    return received["status"], bytes(body)


def unique_path_series():
    samples = []
    for metric in HTTP_REQUESTS_TOTAL.collect():
        for sample in metric.samples:
            if sample.name == "http_requests_total":
                samples.append(sample.labels.get("path", ""))
    return sorted(set(samples))


def main():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        err_status, _ = asyncio.run(asgi_request("GET", "/debug/error"))
        error_logs = [ln for ln in stream.getvalue().splitlines() if "ERROR" in ln or "unhandled exception" in ln]
        print("S1_DEBUG_ERROR_STATUS", err_status)
        print("S1_ERROR_LOG_COUNT", len(error_logs))
        print("S1_SILENT_500", err_status == 500 and len(error_logs) == 0)

        print("S1_READY_HTTP_SKIPPED", "engine.connect hangs; do not call /ready in this environment")
    finally:
        logger.removeHandler(handler)

    before = unique_path_series()
    print("S2_PATHS_BEFORE", before)
    for i in range(12):
        asyncio.run(asgi_request("GET", f"/ghost/{i}"))
    after = unique_path_series()
    ghost_paths = [p for p in after if p.startswith("/ghost/")]
    print("S2_GHOST_PATH_LABELS", ghost_paths)
    print("S2_GHOST_UNIQUE_COUNT", len(ghost_paths))
    print("S2_CARDINALITY_BOMB_ON_RAW_PATH", len(ghost_paths) == 12)

    stream2 = io.StringIO()
    handler2 = logging.StreamHandler(stream2)
    handler2.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler2)
    try:
        emit_log("info", "link created", short_code="abc123", url="https://example.com")
    finally:
        logger.removeHandler(handler2)
    inner = stream2.getvalue().strip()
    print("S3_INNER_BUSINESS_LOG", inner)
    print("S3_INNER_REQUEST_ID_MISSING", "request_id=-" in inner)


if __name__ == "__main__":
    main()
