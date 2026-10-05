"""Module 08 team collaboration suite. ASGI only. Does not open DATABASE_URL."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import API_KEY_A, API_KEY_B
from app.invitations import memberships, reset_for_tests
from app.activity import reset_for_tests as reset_activity
from app.audit import reset_for_tests as reset_audit
from app.comments import reset_for_tests as reset_comments
from app.scripts.module09_test_suite import call


def post(path, key, payload):
    status, _, body = call(
        "POST",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    return status, json.loads(body.decode() or "{}")


def get(path, key):
    status, _, body = call("GET", path, headers={"X-API-Key": key})
    return status, json.loads(body.decode() or "{}")


def put(path, key, payload):
    status, _, body = call(
        "PUT",
        path,
        body=json.dumps(payload).encode(),
        headers={"X-API-Key": key},
    )
    return status, json.loads(body.decode() or "{}")


def reset():
    reset_for_tests()
    reset_activity()
    reset_comments()
    reset_audit()


def fail(name, detail):
    print(name, "FAIL", detail)
    raise SystemExit(1)


def expect(name, got, want):
    ok = got == want
    print(name, got, "OK" if ok else f"WANT_{want}")
    if not ok:
        raise SystemExit(1)


def main():
    reset()

    unauth, _ = post("/teams", "", {"name": "x"})
    expect("E_TEAMS_UNAUTH", unauth, 401)
    empty, _ = post("/teams", API_KEY_A, {"name": ""})
    expect("E_TEAMS_EMPTY_NAME", empty, 400)
    s, team = post("/teams", API_KEY_A, {"name": "ship"})
    expect("E_TEAMS_CREATE", s, 200)
    if team.get("owner") != "principal-a":
        fail("E_TEAMS_OWNER", team.get("owner"))
    tid = team["id"]

    b_inv, _ = post(f"/teams/{tid}/invitations", API_KEY_B, {"email": "z@example.com"})
    expect("P_MEMBER_CANNOT_INVITE_BEFORE_JOIN", b_inv, 403)

    dup1, first = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "member"},
    )
    expect("E_INVITE_OK", dup1, 200)
    dup2, _ = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "member"},
    )
    expect("E_INVITE_DUPLICATE", dup2, 409)
    already, _ = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "a@example.com", "role": "member"},
    )
    expect("E_INVITE_ALREADY_MEMBER", already, 409)
    owner_role, _ = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "other@example.com", "role": "owner"},
    )
    expect("P_INVITE_OWNER_ROLE", owner_role, 400)

    acc, _ = post(f"/invitations/{first.get('token')}/accept", API_KEY_B, {})
    expect("E_ACCEPT_OK", acc, 200)
    expect("E_B_ROLE_MEMBER", memberships.get((tid, "principal-b")), "member")

    member_invite, _ = post(
        f"/teams/{tid}/invitations",
        API_KEY_B,
        {"email": "c@example.com", "role": "viewer"},
    )
    expect("P_MEMBER_CANNOT_INVITE", member_invite, 403)
    member_put, _ = put(
        f"/teams/{tid}/members/principal-a",
        API_KEY_B,
        {"role": "viewer"},
    )
    expect("P_MEMBER_CANNOT_CHANGE_ROLES", member_put, 403)

    com, comment = post(
        f"/teams/{tid}/comments",
        API_KEY_B,
        {"body": "hello @principal-a"},
    )
    expect("P_MEMBER_CAN_COMMENT", com, 200)
    listed, body = get(f"/teams/{tid}/comments", API_KEY_A)
    expect("P_OWNER_CAN_VIEW_COMMENTS", listed, 200)
    if not any(row.get("id") == comment.get("id") for row in (body.get("items") or [])):
        fail("P_COMMENT_VISIBLE", body)

    reset()
    _, team = post("/teams", API_KEY_A, {"name": "view"})
    tid = team["id"]
    inv_s, inv = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "viewer"},
    )
    expect("P_VIEWER_INVITE", inv_s, 200)
    acc_s, _ = post(f"/invitations/{inv.get('token')}/accept", API_KEY_B, {})
    expect("P_VIEWER_ACCEPT", acc_s, 200)
    v_com, _ = post(f"/teams/{tid}/comments", API_KEY_B, {"body": "nope"})
    expect("P_VIEWER_CANNOT_COMMENT", v_com, 403)
    v_inv, _ = post(f"/teams/{tid}/invitations", API_KEY_B, {"email": "x@example.com"})
    expect("P_VIEWER_CANNOT_INVITE", v_inv, 403)
    v_put, _ = put(f"/teams/{tid}/members/principal-b", API_KEY_B, {"role": "admin"})
    expect("P_VIEWER_CANNOT_SELF_ADMIN", v_put, 403)
    v_list, listed = get(f"/teams/{tid}/invitations", API_KEY_B)
    expect("P_VIEWER_CAN_VIEW_LIST", v_list, 200)
    tokens = [row.get("token") for row in (listed.get("items") or [])]
    if any(tokens):
        fail("P_VIEWER_LIST_NO_TOKEN", tokens)

    reset()
    _, secret = post("/teams", API_KEY_A, {"name": "secret"})
    sid = secret["id"]
    cross = []
    cross.append(post(f"/teams/{sid}/invitations", API_KEY_B, {"email": "z@example.com"})[0])
    cross.append(post(f"/teams/{sid}/comments", API_KEY_B, {"body": "x"})[0])
    cross.append(get(f"/teams/{sid}/audit", API_KEY_B)[0])
    cross.append(get(f"/teams/{sid}/invitations", API_KEY_B)[0])
    print("X_CROSS_STATUSES", cross)
    expect("X_CROSS_ALL_DENIED", all(s in (401, 403, 404) for s in cross), True)

    reset()
    _, team = post("/teams", API_KEY_A, {"name": "e2e"})
    tid = team["id"]
    _, inv = post(
        f"/teams/{tid}/invitations",
        API_KEY_A,
        {"email": "b@example.com", "role": "member"},
    )
    post(f"/invitations/{inv.get('token')}/accept", API_KEY_B, {})
    post(f"/teams/{tid}/comments", API_KEY_B, {"body": "task note @principal-a"})
    _, comments = get(f"/teams/{tid}/comments", API_KEY_A)
    _, audit = get(f"/teams/{tid}/audit", API_KEY_A)
    items = audit.get("items") or []
    types = {(row.get("resource_type"), row.get("action")) for row in items}
    print("I_AUDIT_PAIRS", sorted(types))
    expect("I_TEAM_CREATED", ("team", "created") in types, True)
    expect("I_INVITE_CREATED", ("invitation", "created") in types, True)
    expect("I_INVITE_ACCEPTED", ("invitation", "accepted") in types, True)
    expect("I_COMMENT_CREATED", ("comment", "created") in types, True)
    expect("I_MENTION", any(row.get("action") == "notify" for row in items), True)
    expect("I_COMMENT_COUNT", len(comments.get("items") or []), 1)
    expect("I_B_MEMBER", memberships.get((tid, "principal-b")), "member")

    m09 = subprocess.run(
        [sys.executable, "-m", "app.scripts.module09_test_suite"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    expect("I_MODULE09_EXIT", m09.returncode, 0)
    print("MODULE08_TEAM_SUITE_OK True")


if __name__ == "__main__":
    main()
