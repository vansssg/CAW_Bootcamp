import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text

from app.config import DATABASE_URL

print("URL_HOST_HINT", "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL)

t0 = time.perf_counter()
try:
    e = create_engine(
        DATABASE_URL,
        future=True,
        connect_args={"connect_timeout": 1},
    )
    with e.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("SIM2_RESULT", "CONNECTED")
except Exception as exc:
    elapsed = time.perf_counter() - t0
    print("SIM2_RESULT", type(exc).__name__)
    print("SIM2_ELAPSED_S", round(elapsed, 3))
    print("SIM2_MESSAGE", str(exc).splitlines()[0][:300])
else:
    print("SIM2_ELAPSED_S", round(time.perf_counter() - t0, 3))
