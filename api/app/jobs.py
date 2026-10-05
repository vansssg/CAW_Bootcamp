import hashlib
import queue
import threading
import time
from datetime import datetime, timedelta, timezone

from app.cache import analytics_dedup_mark, analytics_dedup_seen

RETENTION_DAYS = 30
MAX_EVENTS = 10_000
MAX_SEEN_JOB_IDS = 10_000
JOB_RETRY_MAX = 5
JOB_BACKOFF_BASE_S = 0.1  # 0.1, 0.2, 0.4, 0.8, 1.6 — same doubling as 1/2/4/8/16
_jobs: queue.Queue = queue.Queue()
_events: list[dict] = []
_seen_job_ids: set[str] = set()
_dead_letter: list[dict] = []
_queue_down = False
_lock = threading.Lock()
_persist = None
_worker_started = False


def hash_ip(ip: str) -> str:
    return hashlib.sha256((ip or "0.0.0.0").encode("utf-8")).hexdigest()[:16]


def set_queue_down(down: bool) -> None:
    global _queue_down
    _queue_down = down


def set_persist_for_tests(fn) -> None:
    global _persist
    _persist = fn


def retry_delays_s(max_retries: int = JOB_RETRY_MAX, base: float = JOB_BACKOFF_BASE_S) -> list[float]:
    return [base * (2**attempt) for attempt in range(max_retries)]


def enqueue_click(job: dict) -> str:
    if _queue_down:
        return "dropped"
    _jobs.put(job)
    return "queued"


def persist_click(job: dict) -> None:
    """Worker-pool persist. Default is a no-op so a down Postgres cannot stall every click.

    Set JOB_PERSIST_DB=1 to attempt SELECT 1 on worker_engine. Tests inject set_persist_for_tests.
    """
    import os

    if _persist is not None:
        _persist(job)
        return
    if os.getenv("JOB_PERSIST_DB", "").lower() not in {"1", "true", "yes"}:
        return
    from sqlalchemy import text

    from app.db import worker_engine

    with worker_engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def _write_event(job: dict) -> str:
    job_id = str(job.get("job_id") or "")
    if analytics_dedup_seen(job_id):
        return "duplicate"
    analytics_dedup_mark(job_id)
    with _lock:
        if job_id in _seen_job_ids:
            return "duplicate"
        _seen_job_ids.add(job_id)
        if len(_seen_job_ids) > MAX_SEEN_JOB_IDS:
            extra = len(_seen_job_ids) - MAX_SEEN_JOB_IDS
            for _ in range(extra):
                _seen_job_ids.pop()
        _events.append(dict(job))
        if len(_events) > MAX_EVENTS:
            del _events[0 : len(_events) - MAX_EVENTS]
        return "written"


def purge_events_for_code(code: str) -> int:
    removed = 0
    with _lock:
        kept = []
        for event in _events:
            if event.get("short_code") == code:
                removed += 1
            else:
                kept.append(event)
        _events[:] = kept
    return removed


def process_job(job: dict, *, persist_db: bool = False) -> str:
    """Memory write. Optional DB persist uses the worker pool, not the API pool."""
    if persist_db:
        persist_click(job)
    return _write_event(job)


def process_job_with_retry(job: dict) -> str:
    last_error = None
    delays = []
    for attempt in range(JOB_RETRY_MAX + 1):
        try:
            persist_click(job)
            return _write_event(job)
        except Exception as exc:
            last_error = exc
            if attempt >= JOB_RETRY_MAX:
                break
            delay = JOB_BACKOFF_BASE_S * (2**attempt)
            delays.append(round(delay, 4))
            from app.main import emit_log

            emit_log(
                "warn",
                "job_retry_backoff",
                attempt=attempt + 1,
                max_retries=JOB_RETRY_MAX,
                delay_ms=int(delay * 1000),
                error_type=type(exc).__name__,
                job_id=job.get("job_id"),
            )
            time.sleep(delay)
    with _lock:
        _dead_letter.append(
            {
                "job": dict(job),
                "error_type": type(last_error).__name__ if last_error else "unknown",
                "attempts": JOB_RETRY_MAX + 1,
                "delays_s": delays,
            }
        )
    from app.main import emit_log

    emit_log(
        "error",
        "job_dead_letter",
        job_id=job.get("job_id"),
        attempts=JOB_RETRY_MAX + 1,
        error_type=type(last_error).__name__ if last_error else "unknown",
    )
    return "dead_letter"


def dead_letters() -> list[dict]:
    with _lock:
        return list(_dead_letter)


def drain_once() -> int:
    processed = 0
    while True:
        try:
            job = _jobs.get_nowait()
        except queue.Empty:
            break
        process_job(job, persist_db=False)
        processed += 1
        _jobs.task_done()
    return processed


def events_for(code: str, start: datetime | None = None, end: datetime | None = None) -> list[dict]:
    out = []
    for event in _events:
        if event.get("short_code") != code:
            continue
        ts = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        out.append(event)
    return out


def purge_old(now: datetime | None = None, retention_days: int = RETENTION_DAYS) -> int:
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=retention_days)
    removed = 0
    kept = []
    with _lock:
        for event in _events:
            ts = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
            if ts < cutoff:
                removed += 1
            else:
                kept.append(event)
        _events[:] = kept
    return removed


def insert_event_for_tests(event: dict) -> None:
    with _lock:
        _events.append(event)


def reset_for_tests() -> None:
    global _queue_down, _persist
    _queue_down = False
    _persist = None
    with _lock:
        _events.clear()
        _seen_job_ids.clear()
        _dead_letter.clear()
    while True:
        try:
            _jobs.get_nowait()
        except queue.Empty:
            break


def start_worker() -> None:
    global _worker_started
    if _worker_started:
        return
    _worker_started = True

    def _loop():
        while True:
            job = _jobs.get()
            try:
                process_job_with_retry(job)
            finally:
                _jobs.task_done()

    thread = threading.Thread(target=_loop, name="click-worker", daemon=True)
    thread.start()


start_worker()
