import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.main import links
from app.ratelimit import reset_for_tests as reset_rates
from app.search import FTS_SELECT_SQL
from app.scripts.module08_search_verify import create, search


def main():
    reset_rates()
    links.clear()
    create("https://www.example.com/one", API_KEY_A, ["docs"])
    create("https://www.example.com/two", API_KEY_A, ["docs"])
    create("https://www.example.com/three", API_KEY_A, ["docs"])

    all_items = search(API_KEY_A, q="example", page=1, page_size=10)
    codes = [i["short_code"] for i in all_items[1].get("items") or []]
    print("FIX_ALL_TOTAL", all_items[1].get("total"), "FIX_ALL_COUNT", len(codes))
    print("FIX_FIRST_PAGE_FULL", len(codes) == 3)

    p1 = search(API_KEY_A, q="example", page=1, page_size=1)
    p1_code = (p1[1].get("items") or [{}])[0].get("short_code")
    p3 = search(API_KEY_A, q="example", page=3, page_size=1)
    p3_code = (p3[1].get("items") or [{}])[0].get("short_code")
    p4 = search(API_KEY_A, q="example", page=4, page_size=1)
    print("FIX_P1_IS_FIRST", p1_code == (codes[0] if codes else None))
    print("FIX_LAST_PAGE_COUNT", len(p3[1].get("items") or []))
    print("FIX_LAST_IS_LAST", p3_code == (codes[-1] if codes else None))
    print("FIX_PAST_END_COUNT", len(p4[1].get("items") or []), "TOTAL", p4[1].get("total"))
    print("FIX_OFFSET_FORMULA", "(page - 1) * page_size")

    inj = search(API_KEY_A, q="example", sort="clicks;drop")
    print("FIX_INJECT_SORT_STATUS", inj[0])
    print("FIX_FTS_BOUND", ":q" in FTS_SELECT_SQL and "plainto_tsquery" in FTS_SELECT_SQL)


if __name__ == "__main__":
    main()
