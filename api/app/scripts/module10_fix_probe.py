"""Module 10 FIX: liveness is /live; /ready stays a dependency signal."""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.scripts.module05_failure_fix_verify import asgi_request


def main():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    railway = (REPO / "railway.toml").read_text(encoding="utf-8")
    main_py = (ROOT / "app/main.py").read_text(encoding="utf-8")
    hc_blob = dockerfile.split("HEALTHCHECK", 1)[-1][:400]
    docker_target = "/ready" if "/ready" in hc_blob else ("/live" if "/live" in hc_blob else "unknown")
    railway_target = "/ready" if 'healthcheckPath = "/ready"' in railway else ("/live" if 'healthcheckPath = "/live"' in railway else "unknown")

    live = asyncio.run(asgi_request("GET", "/live"))
    ready = asyncio.run(asgi_request("GET", "/ready"))
    ready_json = json.loads(ready[2].decode() or "{}")
    probe_status = live[0] if docker_target == "/live" else ready[0]

    print("MISCONFIG_WAS", "HEALTHCHECK and railway healthcheckPath = /ready")
    print("DOCKER_HEALTHCHECK_TARGET", docker_target)
    print("RAILWAY_HEALTHCHECK_TARGET", railway_target)
    print("LIVE_STATUS", live[0])
    print("READY_STATUS", ready[0])
    print("READY_DATABASE", (ready_json.get("checks") or {}).get("database"))
    print("PROBE_STATUS_IF_HEALTHCHECK", probe_status)
    print("PLATFORM_WOULD_KILL_SINGLE_CONTAINER", docker_target == "/ready" and ready[0] != 200)
    print("SHUTDOWN_HANDLER", "def on_shutdown" in main_py)
    print("GRACEFUL_SHUTDOWN_FLAG", "--timeout-graceful-shutdown 30" in dockerfile)
    print("CONTAINER_RUN", "not_run")
    print("CURL_REPLACEMENT", "ASGI GET /live and GET /ready")


if __name__ == "__main__":
    main()
