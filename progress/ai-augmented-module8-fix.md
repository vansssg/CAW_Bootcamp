# AI-Augmented Engineering Module 08 FIX

Assumption: Settings loaded from a local dotenv file. CI checkout has no `API_KEY_*`. The missing “record” was a principal that cannot be constructed, not a team row in Postgres.

Fix: set dummy CI env on the **test** job (`postgresql+psycopg://…@127.0.0.1`, 32-char distinct keys, JWT not reused as a key). Team suite still creates its own teams after `reset_for_tests`. Did not add Alembic; 5432 is not in the pipeline.

Measured: `FIX_SUITE_EXIT 0`; `FIX_SUITE_OK True`; secret lengths 32; keys distinct. GitHub Actions still not executed from this workspace (not a git repo here).
