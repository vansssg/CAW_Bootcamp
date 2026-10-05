import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.main import links
from app.ratelimit import reset_for_tests as reset_rates
from app.scripts.module08_search_verify import create, search


def main():
    reset_rates()
    links.clear()
    create("https://www.example.com/one", API_KEY_A, ["docs"])
    create("https://www.example.com/two", API_KEY_A, ["docs"])
    create("https://www.example.com/three", API_KEY_A, ["docs"])
    all_items = search(API_KEY_A, q="example", page=1, page_size=10)
    codes = [i["short_code"] for i in all_items[1].get("items") or []]
    print("ALL_TOTAL", all_items[1].get("total"), "ALL_COUNT", len(codes))
    p1 = search(API_KEY_A, q="example", page=1, page_size=1)
    p1_code = (p1[1].get("items") or [{}])[0].get("short_code")
    p2 = search(API_KEY_A, q="example", page=2, page_size=1)
    p2_code = (p2[1].get("items") or [{}])[0].get("short_code")
    print("P1_CODE", p1_code, "P1_COUNT", len(p1[1].get("items") or []))
    print("P2_CODE", p2_code, "P2_COUNT", len(p2[1].get("items") or []))
    print("P1_IS_SECOND", p1_code == (codes[1] if len(codes) > 1 else None))
    print("P1_SKIPPED_FIRST", p1_code != (codes[0] if codes else None))
    print("EMPTY_LAST_WHEN_PAGE_EQ_TOTAL", len((search(API_KEY_A, q="example", page=3, page_size=1)[1].get("items") or [])))


if __name__ == "__main__":
    main()
