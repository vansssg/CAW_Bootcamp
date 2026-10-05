# Module 04 BUILD Evidence (Performance Toolbox)

## Scope
Attempted to execute tool-led runtime investigation for:
- Bug #6 memory leak from unclosed DB connections
- Bug #7 N+1 query behavior on links endpoint

## Commands Run and Results

1) Verify API workspace and runtime tooling
- `ls` in `api/` -> confirmed project files present (`alembic/`, `app/`, `requirements.txt`, etc.).
- `ls .venv` in `api/` -> confirmed virtual environment exists with `Scripts/`.

2) Start service for profiling workflow
- Command: `./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 3000`
- Observed output:
  - service startup log printed
  - `INFO: Started server process [...]`
  - `INFO: Waiting for application startup.`
- No readiness completion observed; process remained waiting.

3) Probe API endpoint while startup was waiting
- Command: `curl -sS -m 5 http://127.0.0.1:3000/health`
- Result: connection failed (`Could not connect to server`).

4) Direct DB connectivity test
- Command:
  - `./.venv/Scripts/python.exe -c "from sqlalchemy import create_engine,text; from app.config import DATABASE_URL; e=create_engine(DATABASE_URL,future=True); c=e.connect(); c.execute(text('SELECT 1')); print('DB_OK'); c.close()"`
- Result: command did not complete in the blocking window; remained waiting (no success output).

5) Check local ports required for runtime verification
- Command: `netstat -an | rg "5432|6379|3000"`
- Result: no listening entries returned for Postgres/Redis/API ports.

## What This Proves
- Runtime profiling and query-observation steps could not be completed because required local dependencies were unavailable in this environment at execution time.
- The service did not reach healthy startup, preventing:
  - memory growth profiling under request load
  - query logging/latency experiments for N+1 confirmation

## Limitation (Recorded, Not Fabricated)
- No valid in-process profiler snapshots or DB query logs were produced in this run due to unresolved local runtime dependency availability.

## Non-fabrication note
- All statements above are derived from actual command attempts and observed outputs in this session.
