"""BREAK: silent drop after first WS event (round-3 spiral)."""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.activity import publish, reset_for_tests as reset_activity
from app.auth import API_KEY_A
from app.invitations import reset_for_tests
from app.scripts.module05_activity_verify import _texts, ws_exchange


async def main_async():
    reset_for_tests()
    reset_activity()
    sent, task, done = await ws_exchange(
        "/ws/teams/1/activity",
        {"X-API-Key": API_KEY_A},
        [{"type": "websocket.connect"}],
        drain_after=0.05,
    )
    publish(1, "invitation.created", {"invitation_id": 1})
    await asyncio.sleep(0.05)
    publish(1, "invitation.created", {"invitation_id": 2})
    await asyncio.sleep(0.05)
    texts = _texts(sent)
    types = [row.get("type") for row in texts if isinstance(row, dict)]
    closes = [row.get("close") for row in texts if isinstance(row, dict) and "close" in row]
    print("BREAK_DROP_FLAG", False)
    print("BREAK_EVENT_TYPES", types)
    print("BREAK_FIRST_EVENT_OK", "invitation.created" in types)
    print("BREAK_SECOND_EVENT_MISSING", types.count("invitation.created") < 2)
    print("BREAK_SILENT_CLOSE", bool(closes) or any(m.get("type") == "websocket.close" for m in sent))
    print("BREAK_DIAGNOSIS", "round3_heartbeat_close_after_first_dispatch")
    done.set()
    task.cancel()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
