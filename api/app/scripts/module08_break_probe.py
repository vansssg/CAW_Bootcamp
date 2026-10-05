"""BREAK: local suite green; CI-shaped env (no .env) cannot import the app."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    local = subprocess.run(
        [sys.executable, "-m", "app.scripts.module08_team_suite"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print("BREAK_LOCAL_SUITE_EXIT", local.returncode)
    print("BREAK_LOCAL_SUITE_OK", local.returncode == 0 and "MODULE08_TEAM_SUITE_OK True" in local.stdout)

    env = os.environ.copy()
    for key in (
        "APP_ENV",
        "PORT",
        "DATABASE_URL",
        "REDIS_URL",
        "LOG_LEVEL",
        "JWT_SECRET",
        "CORS_ORIGIN",
        "API_KEY_A",
        "API_KEY_B",
    ):
        env.pop(key, None)
    env["PYTHONPATH"] = str(ROOT)
    # Hide local dotenv file the same way a clean CI checkout without secrets would.
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pydantic_settings import BaseSettings; import os; "
            "os.chdir(r'%s'); "
            "from pathlib import Path; "
            "print('ENVFILE_EXISTS', Path('.env').exists())" % str(ROOT).replace("\\", "\\\\"),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    print("BREAK_DOTENV_PROBE", (probe.stdout or "").strip())

    missing = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os; from pathlib import Path; "
            "p=Path('app/config.py'); "
            "ns={'__file__': str(p.resolve())}; "
            "code=p.read_text(encoding='utf-8'); "
            "os.chdir(r'%s'); "
            "import app.config as c" % str(ROOT).replace("\\", "\\\\"),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    # Import still reads .env from disk. Simulate CI with no file:
    isolated = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pydantic_settings import BaseSettings\n"
            "from pydantic import ValidationError, field_validator, model_validator\n"
            "from enum import Enum\n"
            "class Environment(str, Enum):\n"
            "    development='development'\n"
            "    staging='staging'\n"
            "    production='production'\n"
            "class LogLevel(str, Enum):\n"
            "    debug='debug'; info='info'; warn='warn'; error='error'\n"
            "class Settings(BaseSettings):\n"
            "    model_config = {'extra':'ignore'}\n"
            "    app_env: Environment\n"
            "    port: int\n"
            "    database_url: str\n"
            "    redis_url: str\n"
            "    log_level: LogLevel\n"
            "    jwt_secret: str\n"
            "    cors_origin: str\n"
            "    api_key_a: str\n"
            "    api_key_b: str\n"
            "try:\n"
            "    Settings()\n"
            "    print('BREAK_CI_IMPORT', 'ok')\n"
            "except Exception as exc:\n"
            "    print('BREAK_CI_IMPORT', type(exc).__name__)\n"
            "    print('BREAK_CI_MISSING_ENV', True)\n"
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    print((isolated.stdout or "").strip())
    print("BREAK_CI_STDERR_NONE", not (isolated.stderr or "").strip())
    print("BREAK_ASSUMPTION", "local .env + seed_default_team; CI workflow sets no APP_ENV/API_KEY_*")


if __name__ == "__main__":
    main()
