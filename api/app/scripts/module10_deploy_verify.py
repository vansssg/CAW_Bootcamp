"""Prove Module 10 deploy artifacts without claiming Railway or docker compose up."""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API = ROOT
REPO = ROOT.parent
sys.path.insert(0, str(API))

from app.db import DB_CONNECT_TIMEOUT_S, DB_STATEMENT_TIMEOUT_MS
from app.scripts.module05_failure_fix_verify import asgi_request
import asyncio


def main():
    dockerfile = (API / "Dockerfile").read_text(encoding="utf-8")
    ci = (REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    railway = (REPO / "railway.toml").read_text(encoding="utf-8")
    compose = (REPO / "infra/docker-compose.yml").read_text(encoding="utf-8")
    main_py = (API / "app/main.py").read_text(encoding="utf-8")

    print("DOCKER_HOST_ALL_INTERFACES", "--host 0.0.0.0" in dockerfile)
    print("DOCKER_PORT_FROM_ENV", "${PORT:-3000}" in dockerfile)
    print("DOCKER_HTTP_KEEPALIVE_TIMEOUT", "--timeout-keep-alive 5" in dockerfile)
    print("DOCKER_GRACEFUL_SHUTDOWN_S", "--timeout-graceful-shutdown 30" in dockerfile)
    print("DOCKER_HEALTHCHECK_LIVE", "/live" in dockerfile)
    print("CI_ON_PULL_REQUEST", "pull_request:" in ci)
    print("CI_RUNS_MODULE09", "module09_test_suite.py" in ci)
    print("RAILWAY_HEALTH_LIVE", 'healthcheckPath = "/live"' in railway)
    print("COMPOSE_APP_USES_POSTGRES_HOSTNAME", "postgresql://postgres:postgres@postgres:5432/linkops" in compose)
    print("SHUTDOWN_HANDLER", "def on_shutdown" in main_py and "engine.dispose" in main_py)
    print("MIGRATE_ONE_OFF", (API / "app/scripts/migrate.sh").exists())
    print("DB_CONNECT_TIMEOUT_S", DB_CONNECT_TIMEOUT_S)
    print("DB_STATEMENT_TIMEOUT_MS", DB_STATEMENT_TIMEOUT_MS)

    live = asyncio.run(asgi_request("GET", "/live"))
    ready = asyncio.run(asgi_request("GET", "/ready"))
    print("LIVE_STATUS", live[0])
    print("READY_STATUS", ready[0])
    print("DOCKER_COMPOSE_NOT_CLAIMED", True)


if __name__ == "__main__":
    main()
