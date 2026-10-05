import json
import logging
import os
import re
import time
import traceback
import uuid
from collections import OrderedDict
from contextvars import ContextVar
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel
from sqlalchemy import text
import pybreaker

from app.auth import NOT_OWNER_STATUS, reject_if_not_owner, require_api_key
from app.jobs import (
    RETENTION_DAYS,
    drain_once,
    enqueue_click,
    events_for,
    hash_ip,
    purge_events_for_code,
    purge_old,
)
from app.cache import (
    get_redirect_target,
    invalidate_redirect_target,
    redis_is_down,
    set_redirect_target,
)
from app.config import API_KEY_A, API_KEY_B, APP_ENV, JWT_SECRET, LOG_LEVEL, PORT
from app.db import engine, is_db_unavailable, worker_engine
from app.ratelimit import ANALYTICS_PER_MIN, CREATE_LINK_PER_MIN, REDIRECT_PER_MIN, allow
from app.resilience import db_breaker
from app.search import (
    SEARCH_PAGE_SIZE_DEFAULT,
    SEARCH_PAGE_SIZE_MAX,
    normalize_tag,
    normalize_tags,
    parse_page,
    parse_sort,
    search_links,
)
from app import invitations as invite_mod
from app.activity import activity_socket
from app import comments as comment_mod
from app import audit as audit_mod

audit_mod.ensure_listening()

app = FastAPI()
PROCESS_STARTED_AT = time.monotonic()
logger = logging.getLogger("app")
logger.setLevel(LOG_LEVEL.upper())
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL.upper())
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.propagate = False

# Owner-scoped in-memory store: short_code -> {long_url, owner, clicks}
# Bounded so Module 08 BREAK memory climb cannot run unbounded.
MAX_IN_MEMORY_LINKS = 10_000
links: OrderedDict[str, dict] = OrderedDict()
MAX_URL_LENGTH = 2048
SERVICE_NAME = "url-shortener"
IMAGE_SHA = os.getenv("IMAGE_TAG") or os.getenv("GITHUB_SHA") or "unknown"

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)
URLS_TOTAL = Gauge(
    "urls_total",
    "Number of URLs currently tracked in service memory",
)
URLS_TOTAL.set(0)
REQUEST_ID_CTX: ContextVar[str] = ContextVar("request_id", default="-")


def metric_path(request: Request) -> str:
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    if isinstance(template, str) and template:
        return template
    return "/unmatched"


ERROR_CODES = {
    400: "validation_error",
    401: "unauthenticated",
    403: "forbidden",
    404: "not_found",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
    503: "service_unavailable",
}
REDACT_SECRETS = (
    JWT_SECRET,
    API_KEY_A,
    API_KEY_B,
)


EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def redact_secrets(value: str) -> str:
    redacted = value
    for secret in REDACT_SECRETS:
        if secret and secret in redacted:
            redacted = redacted.replace(secret, "[REDACTED]")
    for marker in ("DO_NOT_LOG_ME_123",):
        if marker in redacted:
            redacted = redacted.replace(marker, "[REDACTED]")
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    return redacted


def error_payload(status: int, message: str, request_id: str, code: str | None = None) -> dict:
    return {
        "error": {
            "code": code or ERROR_CODES.get(status, "error"),
            "message": message,
            "request_id": request_id,
        }
    }


def emit_log(level: str, message: str, request_id: str | None = None, **fields) -> None:
    rid = request_id if request_id is not None else REQUEST_ID_CTX.get()
    if not rid:
        rid = "-"
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "message": message,
        "service_name": SERVICE_NAME,
        "request_id": rid,
    }
    payload.update(fields)
    for key, value in list(payload.items()):
        if isinstance(value, str):
            cleaned = value.replace("\r", "\\r").replace("\n", "\\n")
            payload[key] = redact_secrets(cleaned)
            if key.lower() in {"authorization", "x-api-key", "database_url", "jwt_secret", "api_key"}:
                payload[key] = "[REDACTED]"
    if APP_ENV == "development":
        extras = " ".join(f"{k}={payload[k]}" for k in payload if k not in {"timestamp", "level", "message"})
        rendered = f"{payload['timestamp']} {level.upper()} {message} {extras}".strip()
    else:
        rendered = json.dumps(payload)
    rendered = redact_secrets(rendered)
    log_level = {"error": logging.ERROR, "warn": logging.WARNING, "warning": logging.WARNING}.get(level, logging.INFO)
    logger.log(log_level, rendered)


emit_log("info", "service starting", environment=APP_ENV, port=PORT, log_level=LOG_LEVEL)


class LinkCreate(BaseModel):
    long_url: str
    tags: list[str] = []


class TeamCreate(BaseModel):
    name: str


class InvitationCreate(BaseModel):
    email: str
    role: str = "member"


class MemberRoleUpdate(BaseModel):
    role: str


class CommentCreate(BaseModel):
    body: str
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    body: str


def sanitize_log_value(value: str) -> str:
    return value.replace("\r", "\\r").replace("\n", "\\n")


def extract_bearer_token(auth_header: str | None) -> str:
    if auth_header is None or not isinstance(auth_header, str) or not auth_header.strip():
        raise HTTPException(status_code=401, detail="Authorization required")

    parts = auth_header.strip().split()
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = parts[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")
    return token


def require_admin_auth(request: Request) -> str:
    return require_api_key(request)


def raise_db_unavailable(exc: Exception, action: str) -> None:
    if not is_db_unavailable(exc):
        raise exc
    orig = getattr(exc, "orig", None)
    emit_log(
        "error",
        "database unavailable",
        action=action,
        failure_mode="postgres_connect_or_query_timeout",
        dependency="postgres",
        operation=action,
        timeout_ms=1000,
        error_type=type(orig).__name__ if orig is not None else type(exc).__name__,
    )
    raise HTTPException(status_code=503, detail="service temporarily unavailable")


def call_postgres(action: str, fn, *, fail_closed: bool = True):
    try:
        return db_breaker.call(fn)
    except pybreaker.CircuitBreakerError:
        state = type(db_breaker.current_state).__name__
        emit_log(
            "warn",
            "circuit_open_fallback",
            dependency="postgres",
            action=action,
            circuit_state=state,
        )
        if fail_closed:
            raise HTTPException(status_code=503, detail="service temporarily unavailable")
        return None
    except Exception as exc:
        raise_db_unavailable(exc, action)


@app.middleware("http")
async def structured_request_logging(request: Request, call_next):
    incoming = request.headers.get("x-request-id", "").strip()
    req_id = incoming if incoming else f"req-{uuid.uuid4().hex[:8]}"
    request.state.req_id = req_id
    req_token = REQUEST_ID_CTX.set(req_id)
    start = time.perf_counter()

    try:
        emit_log(
            "info",
            "request received",
            method=request.method,
            path=sanitize_log_value(request.url.path),
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_s = time.perf_counter() - start
            path_label = metric_path(request)
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                path=path_label,
                status="500",
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                path=path_label,
            ).observe(duration_s)
            emit_log(
                "error",
                "unhandled exception",
                method=request.method,
                path=sanitize_log_value(request.url.path),
                status=500,
                duration_ms=int(duration_s * 1000),
                stack_trace=traceback.format_exc(),
            )
            return JSONResponse(
                status_code=500,
                content=error_payload(500, "internal server error", req_id),
                headers={"X-Request-ID": req_id},
            )

        duration_s = time.perf_counter() - start
        duration_ms = int(duration_s * 1000)
        path_label = metric_path(request)

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=path_label,
            status=str(response.status_code),
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=path_label,
        ).observe(duration_s)

        if response.status_code >= 500:
            level, message = "error", "request failed"
        elif response.status_code >= 400:
            level, message = "warn", "request failed"
        else:
            level, message = "info", "request completed"

        emit_log(
            level,
            message,
            method=request.method,
            path=sanitize_log_value(request.url.path),
            status=response.status_code,
            duration_ms=duration_ms,
        )
        response.headers["X-Request-ID"] = req_id
        return response
    finally:
        REQUEST_ID_CTX.reset(req_token)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    req_id = getattr(request.state, "req_id", f"req-{uuid.uuid4().hex[:8]}")
    message = exc.detail if isinstance(exc.detail, str) else "request failed"
    emit_log(
        "error" if exc.status_code >= 500 else "warn",
        "http exception",
        request_id=req_id,
        method=request.method,
        path=sanitize_log_value(request.url.path),
        status=exc.status_code,
        error_detail=sanitize_log_value(message),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.status_code, message, req_id),
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "req_id", f"req-{uuid.uuid4().hex[:8]}")
    emit_log(
        "warn",
        "validation error",
        request_id=req_id,
        method=request.method,
        path=sanitize_log_value(request.url.path),
        status=422,
        error_detail="invalid request",
    )
    return JSONResponse(
        status_code=422,
        content=error_payload(422, "invalid request", req_id),
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "req_id", f"req-{uuid.uuid4().hex[:8]}")
    emit_log(
        "error",
        "unhandled exception",
        request_id=req_id,
        method=request.method,
        path=sanitize_log_value(request.url.path),
        status=500,
        error_type=type(exc).__name__,
        stack_trace=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content=error_payload(500, "internal server error", req_id),
        headers={"X-Request-ID": req_id},
    )


@app.on_event("shutdown")
def on_shutdown():
    emit_log("info", "service shutting down", reason="SIGTERM_or_SIGINT")
    engine.dispose()
    worker_engine.dispose()


@app.on_event("startup")
def verify_database_connection():
    def _startup():
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS analytics (
                        id SERIAL PRIMARY KEY,
                        link_id INTEGER NOT NULL REFERENCES links(id),
                        timestamp_bucket TIMESTAMPTZ NOT NULL,
                        count INTEGER NOT NULL DEFAULT 0,
                        last_accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        CONSTRAINT analytics_link_id_bucket_unique UNIQUE (link_id, timestamp_bucket)
                    )
                    """
                )
            )

    try:
        call_postgres("startup", _startup)
    except HTTPException:
        emit_log(
            "error",
            "startup database check failed",
            action="startup",
            failure_mode="postgres_connect_or_query_timeout",
        )


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/live")
def live():
    return {"ok": True}


def ready_checks():
    """Readiness body for /ready and /readyz. Database is critical; Redis is reported only."""
    checks = {}
    ready_ok = True

    def _ready():
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    try:
        call_postgres("ready", _ready)
        checks["database"] = "connected"
    except HTTPException:
        checks["database"] = "disconnected"
        ready_ok = False

    try:
        checks["cache"] = "disconnected" if redis_is_down() else "connected"
    except Exception:
        checks["cache"] = "disconnected"

    checks["uptime_seconds"] = int(time.monotonic() - PROCESS_STARTED_AT)
    checks["image_sha"] = IMAGE_SHA
    checks["in_memory_links"] = len(links)
    return ready_ok, checks


@app.get("/ready")
@app.get("/readyz")
def ready():
    ready_ok, checks = ready_checks()
    return JSONResponse(
        status_code=200 if ready_ok else 503,
        content={"ok": ready_ok, "checks": checks},
    )


@app.get("/debug/error")
def debug_error():
    if APP_ENV == "production":
        raise HTTPException(status_code=404, detail="Not Found")
    raise RuntimeError("forced observability test error")


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/links")
def create_link(link: LinkCreate, request: Request):
    principal_id = require_api_key(request)
    allow(f"create_link:{principal_id}", CREATE_LINK_PER_MIN)

    if len(link.long_url) > MAX_URL_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"URL is too long. Maximum length is {MAX_URL_LENGTH} characters.",
        )

    parsed = urlparse(link.long_url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=400,
            detail="Only http and https URLs are allowed.",
        )

    try:
        tags = normalize_tags(link.tags)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    short_code = uuid.uuid4().hex[:8]
    while short_code in links:
        short_code = uuid.uuid4().hex[:8]

    links[short_code] = {
        "long_url": link.long_url,
        "owner": principal_id,
        "clicks": 0,
        "tags": tags,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    links.move_to_end(short_code)
    while len(links) > MAX_IN_MEMORY_LINKS:
        links.popitem(last=False)
    URLS_TOTAL.set(len(links))

    # Owner-scoped management store is in-process. Postgres INSERT is not
    # required for 2xx: localhost:5432 is down, and we will not wait ~4s per
    # create or claim a DB write that did not happen.
    emit_log(
        "info",
        "link created",
        short_code=short_code,
        url=sanitize_log_value(link.long_url),
        principal_id=principal_id,
        persisted="memory",
    )

    return {
        "short_code": short_code,
        "long_url": link.long_url,
        "owner": principal_id,
        "tags": tags,
        "persisted": "memory",
    }


@app.get("/links/search")
def search_owned_links(
    request: Request,
    q: str = "",
    tag: str | None = None,
    page: int = 1,
    page_size: int = SEARCH_PAGE_SIZE_DEFAULT,
    sort: str = "created_at",
    order: str = "desc",
):
    """Owner-scoped discovery. Registered before /links/{code} so 'search' is not a short code."""
    principal_id = require_api_key(request)
    try:
        page, page_size = parse_page(page, page_size)
        sort, order = parse_sort(sort, order)
        tag_norm = normalize_tag(tag)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = search_links(
        links,
        owner=principal_id,
        q=q.strip(),
        tag=tag_norm,
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
    )
    emit_log(
        "info",
        "link_search",
        principal_id=principal_id,
        q_len=len(q),
        tag=tag_norm or None,
        page=page,
        page_size=page_size,
        total=result["total"],
        backend=result["backend"],
    )
    return result


@app.get("/links/{code}")
def get_link(code: str, request: Request):
    principal_id = require_api_key(request)
    record = links.get(code)
    if record is None:
        raise HTTPException(status_code=404, detail="Link not found")
    reject_if_not_owner(record.get("owner"), principal_id)
    return {
        "short_code": code,
        "long_url": record["long_url"],
        "owner": record["owner"],
        "clicks": record["clicks"],
    }


@app.get("/links/{code}/analytics")
def get_link_analytics(
    code: str,
    request: Request,
    start: str | None = Query(None, alias="from"),
    end: str | None = Query(None, alias="to"),
):
    principal_id = require_api_key(request)
    allow(f"analytics:{principal_id}", ANALYTICS_PER_MIN)
    record = links.get(code)
    if record is None:
        raise HTTPException(status_code=404, detail="Link not found")
    reject_if_not_owner(record.get("owner"), principal_id)
    drain_once()
    if start:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
    else:
        start_dt = None
    if end:
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
    else:
        end_dt = None
    rows = events_for(code, start_dt, end_dt)
    last = max((row["ts"] for row in rows), default=None)
    sample = rows[-1] if rows else None
    return {
        "short_code": code,
        "clicks": len(rows),
        "last_clicked": last,
        "owner": record["owner"],
        "retention_days": RETENTION_DAYS,
        "ip_hash_sample": None if sample is None else sample.get("ip_hash"),
        "stores_raw_ip": False,
    }


@app.patch("/links/{code}")
def update_link(code: str, link: LinkCreate, request: Request):
    principal_id = require_api_key(request)
    record = links.get(code)
    if record is None:
        raise HTTPException(status_code=404, detail="Link not found")
    reject_if_not_owner(record.get("owner"), principal_id)

    if len(link.long_url) > MAX_URL_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"URL is too long. Maximum length is {MAX_URL_LENGTH} characters.",
        )
    parsed = urlparse(link.long_url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http and https URLs are allowed.")

    record["long_url"] = link.long_url
    invalidate_redirect_target(code)
    emit_log("info", "link updated", short_code=code, principal_id=principal_id)
    return {"short_code": code, "long_url": record["long_url"], "owner": record["owner"]}


@app.delete("/links/{code}")
def delete_owned_link(code: str, request: Request):
    principal_id = require_api_key(request)
    record = links.get(code)
    if record is None:
        raise HTTPException(status_code=404, detail="Link not found")
    reject_if_not_owner(record.get("owner"), principal_id)
    links.pop(code, None)
    invalidate_redirect_target(code)
    purge_events_for_code(code)
    URLS_TOTAL.set(len(links))
    return {"deleted": True, "short_code": code}


@app.get("/r/{code}")
def redirect(code: str, request: Request):
    allow(f"redirect:{code}", REDIRECT_PER_MIN)

    def _enqueue():
        enqueue_click(
            {
                "job_id": getattr(request.state, "req_id", uuid.uuid4().hex),
                "short_code": code,
                "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "user_agent": request.headers.get("user-agent", ""),
                "referrer": request.headers.get("referer", ""),
                "ip_hash": hash_ip(request.client.host if request.client else "0.0.0.0"),
            }
        )

    cached = get_redirect_target(code)
    if cached is not None:
        if code not in links:
            invalidate_redirect_target(code)
            emit_log(
                "warn",
                "cache_sot_mismatch",
                short_code=code,
                reason="source_of_truth_missing",
            )
            raise HTTPException(status_code=404, detail="Link not found")
        _enqueue()
        return RedirectResponse(url=cached, status_code=307)

    memory = links.get(code)
    if memory is not None:
        memory["clicks"] = int(memory.get("clicks") or 0) + 1
        set_redirect_target(code, memory["long_url"])
        emit_log(
            "info",
            "cache_store_fallback",
            short_code=code,
            redis_down=redis_is_down(),
        )
        _enqueue()
        return RedirectResponse(url=memory["long_url"], status_code=307)

    raise HTTPException(status_code=404, detail="Link not found")


@app.post("/api/admin/purge-clicks")
def purge_clicks(request: Request):
    require_admin_auth(request)
    removed = purge_old()
    return {"removed": removed, "retention_days": RETENTION_DAYS}


@app.get("/api/admin/links")
def list_links(request: Request, page: int = 1, limit: int = 10):
    principal_id = require_admin_auth(request)

    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page and limit must be positive integers")
    if limit > SEARCH_PAGE_SIZE_MAX:
        raise HTTPException(
            status_code=400,
            detail=f"limit must be <= {SEARCH_PAGE_SIZE_MAX}",
        )

    owned = [
        {"short_code": code, "original_url": rec["long_url"], "owner": rec["owner"]}
        for code, rec in links.items()
        if rec.get("owner") == principal_id
    ]
    offset = (page - 1) * limit
    page_items = owned[offset : offset + limit]
    return {
        "page": page,
        "limit": limit,
        "count": len(page_items),
        "items": page_items,
        "not_owner_status": NOT_OWNER_STATUS,
    }


@app.delete("/api/admin/links")
def delete_link(request: Request, code: str):
    principal_id = require_admin_auth(request)
    record = links.get(code)
    if record is None:
        raise HTTPException(status_code=404, detail="Link not found")
    reject_if_not_owner(record.get("owner"), principal_id)
    links.pop(code, None)
    invalidate_redirect_target(code)
    purge_events_for_code(code)
    URLS_TOTAL.set(len(links))
    return {"deleted": True, "short_code": code}


@app.post("/teams")
def create_team(body: TeamCreate, request: Request):
    principal_id = require_api_key(request)
    team = invite_mod.create_team(body.name, principal_id)
    emit_log("info", "team created", team_id=team["id"], principal_id=principal_id)
    return team


@app.post("/teams/{team_id}/invitations")
def create_team_invitation(team_id: int, body: InvitationCreate, request: Request):
    principal_id = require_api_key(request)
    result = invite_mod.createInvitation(team_id, body.email, principal_id, body.role)
    emit_log(
        "info",
        "invitation created",
        team_id=team_id,
        email=result.get("email"),
        principal_id=principal_id,
        email_sent=result.get("email_sent"),
    )
    return result


@app.get("/teams/{team_id}/invitations")
def list_team_invitations(team_id: int, request: Request):
    principal_id = require_api_key(request)
    return {"items": invite_mod.listInvitations(team_id, principal_id)}


@app.post("/invitations/{token}/accept")
def accept_team_invitation(token: str, request: Request):
    principal_id = require_api_key(request)
    return invite_mod.acceptInvitation(token, principal_id)


@app.put("/teams/{team_id}/members/{user_id}")
def update_team_member_role(team_id: int, user_id: str, body: MemberRoleUpdate, request: Request):
    principal_id = require_api_key(request)
    return invite_mod.update_member_role(team_id, user_id, principal_id, body.role)


@app.websocket("/ws/teams/{team_id}/activity")
async def team_activity_feed(websocket: WebSocket, team_id: int):
    await activity_socket(websocket, team_id, require_member=invite_mod.require_team_member)


@app.post("/teams/{team_id}/comments")
def create_team_comment(team_id: int, body: CommentCreate, request: Request):
    principal_id = require_api_key(request)
    return comment_mod.create_comment(team_id, principal_id, body.body, body.parent_id)


@app.get("/teams/{team_id}/comments")
def list_team_comments(team_id: int, request: Request):
    principal_id = require_api_key(request)
    return {"items": comment_mod.list_comments(team_id, principal_id)}


@app.patch("/teams/{team_id}/comments/{comment_id}")
def update_team_comment(team_id: int, comment_id: int, body: CommentUpdate, request: Request):
    principal_id = require_api_key(request)
    return comment_mod.update_comment(team_id, comment_id, principal_id, body.body)


@app.delete("/teams/{team_id}/comments/{comment_id}")
def delete_team_comment(team_id: int, comment_id: int, request: Request):
    principal_id = require_api_key(request)
    return comment_mod.delete_comment(team_id, comment_id, principal_id)


@app.get("/teams/{team_id}/audit")
def list_team_audit(team_id: int, request: Request):
    principal_id = require_api_key(request)
    invite_mod.require_team_member(team_id, principal_id)
    return {"items": audit_mod.list_for_team(team_id)}