import time
from collections import defaultdict, deque

from fastapi import HTTPException

# decisions.module_04.rate_limits
CREATE_LINK_PER_MIN = 5
REDIRECT_PER_MIN = 8
ANALYTICS_PER_MIN = 5
WINDOW_S = 60.0

_hits: dict[str, deque[float]] = defaultdict(deque)


def allow(bucket: str, limit: int) -> None:
    now = time.monotonic()
    q = _hits[bucket]
    while q and now - q[0] > WINDOW_S:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    q.append(now)


def reset_for_tests() -> None:
    _hits.clear()
