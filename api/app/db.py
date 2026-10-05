from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, TimeoutError as SATimeoutError
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

DB_CONNECT_TIMEOUT_S = 1
DB_STATEMENT_TIMEOUT_MS = 1000
API_POOL_SIZE = 5
WORKER_POOL_SIZE = 2


def _engine(pool_size: int, name: str):
    return create_engine(
        DATABASE_URL,
        future=True,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=0,
        pool_timeout=DB_CONNECT_TIMEOUT_S,
        connect_args={
            "connect_timeout": DB_CONNECT_TIMEOUT_S,
            "options": f"-c statement_timeout={DB_STATEMENT_TIMEOUT_MS}",
        },
    )


# Bulkhead: API and queue worker must not share a QueuePool.
engine = _engine(API_POOL_SIZE, "api")
worker_engine = _engine(WORKER_POOL_SIZE, "worker")
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def is_db_unavailable(exc: BaseException) -> bool:
    return isinstance(exc, (OperationalError, SATimeoutError))
