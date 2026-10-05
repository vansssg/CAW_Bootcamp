"""FIX: writer no longer closes after first event."""

import asyncio
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
    types = [row.get("type") for row in _texts(sent) if isinstance(row, dict)]
    created = types.count("invitation.created")
    print("FIX_EVENT_CREATED_COUNT", created)
    print("FIX_BOTH_EVENTS", created >= 2)
    print("FIX_NO_CLOSE_AFTER_FIRST", not any(
        m.get("type") == "websocket.close" for m in sent
    ))
    done.set()
    task.cancel()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
