import asyncio
import io
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import HTTP_REQUESTS_TOTAL, REQUEST_ID_CTX, app, emit_log


async def asgi_request(method: str, path: str, headers=None):
    body = bytearray()
    received = {"status": None, "headers": []}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            received["status"] = message["status"]
            received["headers"] = message.get("headers", [])
        elif message["type"] == "http.response.body":
            body.extend(message.get("body", b""))

    header_list = []
    for key, value in (headers or {}).items():
        header_list.append((key.lower().encode("latin-1"), value.encode("latin-1")))
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
    return received["status"], header_map, bytes(body)


def series():
    rows = []
    for metric in HTTP_REQUESTS_TOTAL.collect():
        for sample in metric.samples:
            if sample.name == "http_requests_total":
                rows.append((sample.labels.get("path"), sample.labels.get("status"), sample.value))
    return rows


def main():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        for i in range(12):
            asyncio.run(asgi_request("GET", f"/ghost/{i}"))
        err_status, err_headers, _ = asyncio.run(
            asgi_request("GET", "/debug/error", headers={"x-request-id": "req-fix-500"})
        )
        asyncio.run(asgi_request("GET", "/live"))
        token = REQUEST_ID_CTX.set("req-fix-inner")
        try:
            emit_log("info", "link created", short_code="abc123")
        finally:
            REQUEST_ID_CTX.reset(token)
    finally:
        logger.removeHandler(handler)

    logs = stream.getvalue()
    ghost = [p for p, _, _ in series() if p and p.startswith("/ghost/")]
    unmatched = [(p, s, v) for p, s, v in series() if p == "/unmatched"]
    debug_500 = [(p, s, v) for p, s, v in series() if p == "/debug/error" and s == "500"]
    print("FIX_GHOST_RAW_PATH_SERIES", ghost)
    print("FIX_UNMATCHED_SERIES", unmatched)
    print("FIX_CARDINALITY_COLLAPSED", len(ghost) == 0)
    print("FIX_DEBUG_ERROR_STATUS", err_status)
    print("FIX_DEBUG_ERROR_REQUEST_ID", err_headers.get("x-request-id"))
    print("FIX_DEBUG_500_METRIC", debug_500)
    print("FIX_ERROR_LOG_HAS_STACK", "RuntimeError: forced observability test error" in logs)
    print("FIX_ERROR_LOG_HAS_REQUEST_ID", "req-fix-500" in logs)
    print("FIX_INNER_LOG_INHERITS_REQUEST_ID", "request_id=req-fix-inner" in logs)
    total_500 = sum(v for _, s, v in series() if s == "500")
    total_all = sum(v for _, _, v in series())
    print("FIX_500_COUNT", total_500)
    print("FIX_TOTAL_COUNT", total_all)
    print("FIX_ERROR_RATE", (total_500 / total_all) if total_all else None)
    print("FIX_HIGH_ERROR_RATE_WOULD_FIRE", (total_500 / total_all) > 0.05 if total_all else False)
    print("FIX_NOTE", "rule is rate > 0.05 for 2m; this process snapshot is not a Prometheus for: 2m evaluation")


if __name__ == "__main__":
    main()
