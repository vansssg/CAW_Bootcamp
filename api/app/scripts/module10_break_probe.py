"""Module 10 BREAK: platform healthcheck on /ready while Postgres is unreachable."""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.scripts.module05_failure_fix_verify import asgi_request


def probe_target(text: str) -> str:
    if "/ready" in text and "/live" not in text.split("HEALTHCHECK")[-1][:400]:
        if 'healthcheckPath = "/ready"' in text or "/ready'" in text or '/ready"' in text:
            return "/ready"
    if 'healthcheckPath = "/ready"' in text:
        return "/ready"
    if 'healthcheckPath = "/live"' in text:
        return "/live"
    if "/ready" in text:
        return "/ready"
    if "/live" in text:
        return "/live"
    return "unknown"


def main():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    railway = (REPO / "railway.toml").read_text(encoding="utf-8")
    ci = (REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    docker_hc = "/ready" if 'urlopen(f\'http://127.0.0.1:{os.getenv("PORT","3000")}/ready\'' in dockerfile.replace(" ", "") or "/ready', timeout=3)" in dockerfile or '/ready", timeout=3)' in dockerfile or "/ready', timeout=3)" in dockerfile else ("/live" if "/live" in dockerfile.split("HEALTHCHECK")[-1][:300] else "unknown")
    # Simpler: substring after HEALTHCHECK
    hc_blob = dockerfile.split("HEALTHCHECK", 1)[-1][:400]
    docker_target = "/ready" if "/ready" in hc_blob else ("/live" if "/live" in hc_blob else "unknown")
    railway_target = "/ready" if 'healthcheckPath = "/ready"' in railway else ("/live" if 'healthcheckPath = "/live"' in railway else "unknown")

    live = asyncio.run(asgi_request("GET", "/live"))
    ready = asyncio.run(asgi_request("GET", "/ready"))
    live_status, _, live_body = live
    ready_status, _, ready_body = ready
    ready_json = json.loads(ready_body.decode() or "{}")

    probe_status = ready_status if docker_target == "/ready" else live_status
    platform_would_kill = docker_target == "/ready" and ready_status != 200

    print("DOCKER_HEALTHCHECK_TARGET", docker_target)
    print("RAILWAY_HEALTHCHECK_TARGET", railway_target)
    print("LIVE_STATUS", live_status)
    print("READY_STATUS", ready_status)
    print("READY_OK", ready_json.get("ok"))
    print("READY_DATABASE", (ready_json.get("checks") or {}).get("database"))
    print("PROBE_STATUS_IF_HEALTHCHECK", probe_status)
    print("PLATFORM_WOULD_KILL_SINGLE_CONTAINER", platform_would_kill)
    print("CI_DEPLOY_REQUIRES_READY_200", 'test "$READY" = "200"' in ci)
    print("RAILWAY_OR_COMPOSE_NOT_RUN", True)


if __name__ == "__main__":
    main()
