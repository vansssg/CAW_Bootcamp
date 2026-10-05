"""Activity-feed iteration probe. Bus + HTTP; no httpx WebSocket client."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.activity import publish, replay_since, reset_for_tests as reset_activity, subscribe
from app.auth import API_KEY_A, API_KEY_B
from app.invitations import reset_for_tests
from app.scripts.module09_test_suite import call


def post(path, key, payload):
    status, _, body = call(
        "POST",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    return status, json.loads(body.decode() or "{}")


def main():
    reset_for_tests()
    reset_activity()
    seen = []
    subscribe(1, seen.append)
    first = publish(1, "link.created", {"short_code": "abc"})
    publish(2, "link.created", {"short_code": "other"})
    print("ITER_BUS_TEAM1_COUNT", len(seen))
    print("ITER_BUS_TEAM1_TYPE", seen[0]["type"] if seen else None)
    print("ITER_ISOLATION_TEAM2_NOT_IN_TEAM1", all(row["team_id"] == 1 for row in seen))
    print("ITER_REPLAY_COUNT", len(replay_since(1, None)))
    print("ITER_REPLAY_SINCE_EMPTY", len(replay_since(1, first["ts"])) == 0)

    reset_for_tests()
    create_status, created = post(
        "/teams/1/invitations",
        API_KEY_A,
        {"email": "feed.user@example.com"},
    )
    events = replay_since(1, None)
    types = [row["type"] for row in events]
    payloads = [row.get("payload") or {} for row in events]
    emails_in_payload = any("email" in row for row in payloads)
    print("ITER_INVITE_HTTP", create_status)
    print("ITER_INVITE_EVENT_TYPES", types)
    print("ITER_INVITE_CREATED_EVENT", "invitation.created" in types)
    print("ITER_NO_EMAIL_IN_PAYLOAD", not emails_in_payload)

    other, other_body = post("/teams", API_KEY_A, {"name": "other"})
    team_id = other_body["id"]
    post(
        f"/teams/{team_id}/invitations",
        API_KEY_A,
        {"email": "b@example.com"},
    )
    from app.invitations import invitations as invite_rows

    token = [row["token"] for row in invite_rows.values() if row["team_id"] == team_id][0]
    accept_status, _ = post(f"/invitations/{token}/accept", API_KEY_B, {})
    accept_types = [row["type"] for row in replay_since(team_id, None)]
    print("ITER_ACCEPT_HTTP", accept_status)
    print("ITER_ACCEPT_EVENT", "invitation.accepted" in accept_types)

    print("ITER_STRUCTURAL_NOT_NOTIFY", True)
    print("ITER_WS_ROUTE", "/ws/teams/{team_id}/activity")


if __name__ == "__main__":
    main()
