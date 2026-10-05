"""First-pass invitation test: happy path only. Intentionally thin."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A
from app.invitations import reset_for_tests
from app.scripts.module09_test_suite import call


def main():
    reset_for_tests()
    status, _, body = call(
        "POST",
        "/teams/1/invitations",
        body=json.dumps({"email": "new.user@example.com"}).encode(),
        headers={"X-API-Key": API_KEY_A},
    )
    data = json.loads(body.decode() or "{}")
    print("HAPPY_STATUS", status)
    print("HAPPY_EMAIL", data.get("email"))
    print("HAPPY_STATUS_FIELD", data.get("status"))
    assert status == 200
    assert data.get("status") == "pending"


if __name__ == "__main__":
    main()
