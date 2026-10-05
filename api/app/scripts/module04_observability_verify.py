import asyncio
import io
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import main as app_main
from app.main import app, emit_log


def capture_emit(level, message, **fields):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        emit_log(level, message, **fields)
    finally:
        logger.removeHandler(handler)
    return stream.getvalue().strip()


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


def main():
    pretty = capture_emit(
        "info",
        "request completed",
        request_id="req-verify01",
        method="GET",
        path="/live",
    )
    print("DEV_PRETTY_LOG", pretty)
    print("DEV_HAS_TIMESTAMP", pretty[:4].isdigit())
    print("DEV_HAS_LEVEL", "INFO" in pretty)
    print("DEV_HAS_MESSAGE", "request completed" in pretty)
    print("DEV_HAS_SERVICE", "service_name=url-shortener" in pretty)
    print("DEV_HAS_REQUEST_ID", "request_id=req-verify01" in pretty)

    orig_env = app_main.APP_ENV
    app_main.APP_ENV = "production"
    try:
        json_line = capture_emit(
            "error",
            "request failed",
            request_id="req-verify02",
            status=500,
            stack_trace="RuntimeError: forced observability test error",
        )
        parsed = json.loads(json_line)
        required = ["timestamp", "level", "message", "service_name", "request_id"]
        print("PROD_JSON_KEYS", sorted(parsed.keys()))
        print("PROD_JSON_REQUIRED_OK", all(k in parsed for k in required))
        print("PROD_JSON_LEVEL", parsed["level"])
        print("PROD_JSON_REQUEST_ID", parsed["request_id"])
        print("PROD_JSON_HAS_STACK", "stack_trace" in parsed)
    finally:
        app_main.APP_ENV = orig_env

    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        statuses = []

        async def drill():
            for _ in range(8):
                status, _, _ = await asgi_request("GET", "/live")
                statuses.append(status)
            health_status, _, _ = await asgi_request("GET", "/health")
            statuses.append(health_status)
            honored_status, honored_headers, _ = await asgi_request(
                "GET",
                "/live",
                headers={"x-request-id": "req-upstream-abc"},
            )
            statuses.append(honored_status)
            err_status, err_headers, err_body = await asgi_request("GET", "/debug/error")
            metrics_status, metrics_headers, metrics_body = await asgi_request("GET", "/metrics")
            return {
                "health_status": health_status,
                "honored_status": honored_status,
                "honored_request_id": honored_headers.get("x-request-id"),
                "err_status": err_status,
                "err_request_id": err_headers.get("x-request-id"),
                "err_body": err_body.decode("utf-8", errors="replace"),
                "metrics_status": metrics_status,
                "metrics_content_type": metrics_headers.get("content-type", ""),
                "metrics_text": metrics_body.decode("utf-8", errors="replace"),
            }

        result = asyncio.run(drill())
    finally:
        logger.removeHandler(handler)

    logs = log_stream.getvalue()
    print("LIVE_STATUSES", statuses)
    print("HEALTH_STATUS", result["health_status"])
    print("HONORED_X_REQUEST_ID", result["honored_request_id"])
    print("DEBUG_ERROR_STATUS", result["err_status"])
    print("DEBUG_ERROR_REQUEST_ID", result["err_request_id"])
    print("DEBUG_ERROR_BODY", result["err_body"])
    print("METRICS_STATUS", result["metrics_status"])
    print("METRICS_CONTENT_TYPE", result["metrics_content_type"])
    text = result["metrics_text"]
    print("METRICS_HAS_COUNTER", "http_requests_total" in text)
    print("METRICS_HAS_HISTOGRAM", "http_request_duration_seconds" in text)
    print("METRICS_HAS_GAUGE", "urls_total" in text)
    live_lines = [
        ln
        for ln in text.splitlines()
        if ln.startswith("http_requests_total{") and 'path="/live"' in ln and 'status="200"' in ln
    ]
    err_lines = [
        ln
        for ln in text.splitlines()
        if ln.startswith("http_requests_total{") and 'path="/debug/error"' in ln and 'status="500"' in ln
    ]
    hist_lines = [
        ln
        for ln in text.splitlines()
        if ln.startswith("http_request_duration_seconds_bucket{")
    ]
    print("METRICS_LIVE_200_LINES", live_lines[:5])
    print("METRICS_500_LINES", err_lines[:5])
    print("METRICS_HISTOGRAM_BUCKET_SAMPLE", hist_lines[:3])
    print("LOG_HAS_ERROR_LEVEL", " ERROR " in logs or '"level": "error"' in logs or "unhandled exception" in logs)
    print("LOG_HAS_STACK", "RuntimeError: forced observability test error" in logs)
    print("LOG_HAS_UPSTREAM_REQUEST_ID", "req-upstream-abc" in logs)
    error_log_lines = [ln for ln in logs.splitlines() if "unhandled exception" in ln or "request failed" in ln]
    print("ERROR_LOG_SAMPLE", error_log_lines[:4])


if __name__ == "__main__":
    main()
