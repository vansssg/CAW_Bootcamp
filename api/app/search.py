"""Owner-scoped link search. DB-native FTS when SEARCH_USE_POSTGRES=1, else in-memory."""

from __future__ import annotations

import os
import re
from typing import Any

from sqlalchemy import text

from app.db import engine, is_db_unavailable

SEARCH_PAGE_SIZE_DEFAULT = 10
SEARCH_PAGE_SIZE_MAX = 50
SORT_ALLOW = frozenset({"created_at", "clicks"})
ORDER_ALLOW = frozenset({"asc", "desc"})
TAG_RE = re.compile(r"^[a-z0-9-]{1,32}$")

FTS_ENSURE_SQL = """
ALTER TABLE links
  ADD COLUMN IF NOT EXISTS search_tsv tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(original_url, '') || ' ' || coalesce(short_code, ''))
  ) STORED
"""

FTS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS links_search_tsv_gin ON links USING GIN (search_tsv)
"""

# sort/order are interpolated only from SORT_ALLOW / ORDER_ALLOW, never from raw query strings.
FTS_SELECT_SQL = """
SELECT short_code, original_url AS long_url, created_by AS owner
FROM links
WHERE created_by = :owner
  AND (:q = '' OR search_tsv @@ plainto_tsquery('english', :q))
  AND (:tag = '' OR :tag = ANY(tags))
ORDER BY {sort} {order}
LIMIT :limit OFFSET :offset
"""

FTS_COUNT_SQL = """
SELECT count(*) AS n
FROM links
WHERE created_by = :owner
  AND (:q = '' OR search_tsv @@ plainto_tsquery('english', :q))
  AND (:tag = '' OR :tag = ANY(tags))
"""


def normalize_tag(value: str | None) -> str:
    if value is None:
        return ""
    tag = str(value).strip().lower()
    if not tag:
        return ""
    if not TAG_RE.fullmatch(tag):
        raise ValueError("tag must be 1-32 chars of [a-z0-9-]")
    return tag


def normalize_tags(raw: list[str] | None) -> list[str]:
    if not raw:
        return []
    out = []
    seen = set()
    for item in raw:
        tag = normalize_tag(item)
        if tag and tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def parse_page(page: int | None, page_size: int | None) -> tuple[int, int]:
    p = 1 if page is None else int(page)
    size = SEARCH_PAGE_SIZE_DEFAULT if page_size is None else int(page_size)
    if p < 1:
        raise ValueError("page must be >= 1")
    if size < 1:
        raise ValueError("page_size must be >= 1")
    if size > SEARCH_PAGE_SIZE_MAX:
        raise ValueError(f"page_size must be <= {SEARCH_PAGE_SIZE_MAX}")
    return p, size


def parse_sort(sort: str | None, order: str | None) -> tuple[str, str]:
    s = (sort or "created_at").strip().lower()
    o = (order or "desc").strip().lower()
    if s not in SORT_ALLOW:
        raise ValueError("sort must be created_at or clicks")
    if o not in ORDER_ALLOW:
        raise ValueError("order must be asc or desc")
    return s, o


def _match_q(record: dict, code: str, q: str) -> bool:
    if not q:
        return True
    needle = q.lower()
    return needle in (record.get("long_url") or "").lower() or needle in code.lower()


def search_memory(
    store: dict[str, dict],
    *,
    owner: str,
    q: str = "",
    tag: str = "",
    page: int = 1,
    page_size: int = SEARCH_PAGE_SIZE_DEFAULT,
    sort: str = "created_at",
    order: str = "desc",
) -> dict[str, Any]:
    rows = []
    for code, rec in store.items():
        if rec.get("owner") != owner:
            continue
        if not _match_q(rec, code, q):
            continue
        if tag and tag not in (rec.get("tags") or []):
            continue
        rows.append(
            {
                "short_code": code,
                "long_url": rec["long_url"],
                "owner": rec["owner"],
                "clicks": int(rec.get("clicks") or 0),
                "created_at": rec.get("created_at") or "",
                "tags": list(rec.get("tags") or []),
            }
        )
    reverse = order == "desc"
    if sort == "clicks":
        rows.sort(key=lambda r: r["clicks"], reverse=reverse)
    else:
        rows.sort(key=lambda r: r["created_at"], reverse=reverse)
    total = len(rows)
    offset = (page - 1) * page_size
    page_items = rows[offset : offset + page_size]
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": page_items,
        "backend": "memory",
    }


def search_postgres(
    *,
    owner: str,
    q: str = "",
    tag: str = "",
    page: int = 1,
    page_size: int = SEARCH_PAGE_SIZE_DEFAULT,
    sort: str = "created_at",
    order: str = "desc",
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    params = {
        "owner": owner,
        "q": q or "",
        "tag": tag or "",
        "limit": page_size,
        "offset": offset,
    }
    select_sql = FTS_SELECT_SQL.format(sort=sort, order=order.upper())
    with engine.begin() as conn:
        conn.execute(text(FTS_ENSURE_SQL))
        conn.execute(text(FTS_INDEX_SQL))
        total = int(conn.execute(text(FTS_COUNT_SQL), params).scalar_one())
        result = conn.execute(text(select_sql), params)
        items = []
        for row in result:
            items.append(
                {
                    "short_code": row.short_code,
                    "long_url": row.long_url,
                    "owner": row.owner,
                    "tags": [],
                }
            )
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items,
        "backend": "postgres_fts",
    }


def search_links(store: dict[str, dict], **kwargs) -> dict[str, Any]:
    if os.getenv("SEARCH_USE_POSTGRES") == "1":
        try:
            return search_postgres(**kwargs)
        except Exception as exc:
            if not is_db_unavailable(exc):
                raise
    return search_memory(store, **kwargs)
