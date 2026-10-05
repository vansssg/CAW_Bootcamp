"""FIX: CI dummy env is enough to import Settings and run the team suite."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CI_ENV = {
    "APP_ENV": "development",
    "PORT": "3000",
    "DATABASE_URL": "postgresql+psycopg://ci:ci@127.0.0.1:5432/ci",
    "REDIS_URL": "redis://127.0.0.1:6379/0",
    "LOG_LEVEL": "info",
    "JWT_SECRET": "ci-jwt-secret-value-at-least-32c",
    "CORS_ORIGIN": "http://localhost:3000",
    "API_KEY_A": "ci-test-api-key-a-at-least-32chx",
    "API_KEY_B": "ci-test-api-key-b-at-least-32chy",
}


def main():
    env = os.environ.copy()
    env.update(CI_ENV)
    env["PYTHONPATH"] = str(ROOT)
    lengths = {k: len(v) for k, v in CI_ENV.items() if k in {"JWT_SECRET", "API_KEY_A", "API_KEY_B"}}
    print("FIX_CI_SECRET_LEN", lengths)
    print("FIX_CI_KEYS_DISTINCT", CI_ENV["API_KEY_A"] != CI_ENV["API_KEY_B"])
    print("FIX_JWT_NOT_AN_API_KEY", CI_ENV["JWT_SECRET"] not in {CI_ENV["API_KEY_A"], CI_ENV["API_KEY_B"]})

    suite = subprocess.run(
        [sys.executable, "-m", "app.scripts.module08_team_suite"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    print("FIX_SUITE_EXIT", suite.returncode)
    print("FIX_SUITE_OK", suite.returncode == 0 and "MODULE08_TEAM_SUITE_OK True" in suite.stdout)
    if suite.returncode != 0:
        print((suite.stdout or "")[-500:])
        print((suite.stderr or "")[-500:])
        raise SystemExit(suite.returncode)


if __name__ == "__main__":
    main()
