import time

from app.config import REDIS_URL

TTL_S = 60
MAX_LOCAL = 1000
REDIRECT_PREFIX = "link:redirect:"
DEDUP_PREFIX = "analytics:dedup:"
_local: dict[str, tuple[str, float]] = {}
_redis = None
_probed = False
_redis_down = True


def redirect_cache_key(code: str) -> str:
    return f"{REDIRECT_PREFIX}{code}"


def analytics_dedup_key(job_id: str) -> str:
    return f"{DEDUP_PREFIX}{job_id}"


def _log(level: str, message: str, **fields) -> None:
    from app.main import emit_log

    emit_log(level, message, **fields)


def _client():
    global _redis, _probed, _redis_down
    if _probed:
        return _redis
    _probed = True
    try:
        import redis as redis_lib

        client = redis_lib.Redis.from_url(
            REDIS_URL,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
            decode_responses=True,
        )
        client.ping()
        _redis = client
        _redis_down = False
        _log("info", "cache_redis_up", backend="redis")
    except Exception as exc:
        _redis = None
        _redis_down = True
        _log(
            "warn",
            "cache_redis_down_fallback",
            backend="memory",
            error_type=type(exc).__name__,
        )
    return _redis


def redis_is_down() -> bool:
    _client()
    return _redis_down


def _local_get(key: str) -> str | None:
    entry = _local.get(key)
    if entry is None:
        return None
    value, expires = entry
    if expires < time.monotonic():
        _local.pop(key, None)
        return None
    return value


def _local_set(key: str, value: str, ttl_seconds: int) -> None:
    _local[key] = (value, time.monotonic() + ttl_seconds)
    if len(_local) > MAX_LOCAL:
        now = time.monotonic()
        expired = [k for k, (_, exp) in _local.items() if exp < now]
        for k in expired:
            _local.pop(k, None)
        while len(_local) > MAX_LOCAL:
            _local.pop(next(iter(_local)))


def get_redirect_target(code: str) -> str | None:
    key = redirect_cache_key(code)
    client = _client()
    if client is not None:
        try:
            value = client.get(key)
            if value:
                _log("info", "cache_hit", short_code=code, backend="redis", cache_key=key)
                return value
            _log("info", "cache_miss", short_code=code, backend="redis", cache_key=key)
            return None
        except Exception as exc:
            _log("warn", "cache_redis_down_fallback", error_type=type(exc).__name__)

    value = _local_get(key)
    if value is None:
        _log("info", "cache_miss", short_code=code, backend="memory", cache_key=key)
        return None
    _log("info", "cache_hit", short_code=code, backend="memory", cache_key=key)
    return value


def set_redirect_target(code: str, url: str, ttl_seconds: int = TTL_S) -> None:
    key = redirect_cache_key(code)
    client = _client()
    if client is not None:
        try:
            client.setex(key, ttl_seconds, url)
            _log("info", "cache_set", short_code=code, backend="redis", cache_key=key, ttl_s=ttl_seconds)
            return
        except Exception as exc:
            _log("warn", "cache_redis_down_fallback", error_type=type(exc).__name__)
    _local_set(key, url, ttl_seconds)
    _log("info", "cache_set", short_code=code, backend="memory", cache_key=key, ttl_s=ttl_seconds)


def invalidate_redirect_target(code: str) -> None:
    """Delete only link:redirect:<code>. Must not touch analytics:dedup:*."""
    key = redirect_cache_key(code)
    client = _client()
    if client is not None:
        try:
            client.delete(key)
        except Exception as exc:
            _log("warn", "cache_redis_down_fallback", error_type=type(exc).__name__)
    _local.pop(key, None)
    _log("info", "cache_invalidate", short_code=code, cache_key=key)


def analytics_dedup_seen(job_id: str) -> bool:
    key = analytics_dedup_key(job_id)
    client = _client()
    if client is not None:
        try:
            return bool(client.get(key))
        except Exception as exc:
            _log("warn", "cache_redis_down_fallback", error_type=type(exc).__name__)
    return _local_get(key) is not None


def analytics_dedup_mark(job_id: str, ttl_seconds: int = 86400) -> None:
    key = analytics_dedup_key(job_id)
    client = _client()
    if client is not None:
        try:
            client.setex(key, ttl_seconds, "1")
            return
        except Exception as exc:
            _log("warn", "cache_redis_down_fallback", error_type=type(exc).__name__)
    _local_set(key, "1", ttl_seconds)


def namespace_keys() -> dict:
    redirect = [k for k in _local if k.startswith(REDIRECT_PREFIX)]
    dedup = [k for k in _local if k.startswith(DEDUP_PREFIX)]
    return {"redirect": redirect, "dedup": dedup}


def reset_for_tests() -> None:
    _local.clear()
