# AI-Augmented Engineering Module 08 BREAK

Local `module08_team_suite` is green. A CI-shaped process with **no env vars** cannot construct Settings (`BREAK_CI_IMPORT ValidationError`). `.github/workflows/ci.yml` never sets `API_KEY_*` / `APP_ENV`. This machine has `api/.env` (`ENVFILE_EXISTS True`).

That is the missing record: not a team row in Postgres (5432 not serving). It is the **config principal** the app loads from a local dotenv file the pipeline does not have.

Second local assumption: `seed_default_team` creates team 1 with B as member on import. Older probes hit `/teams/1`. The new suite creates its own teams; CI would still die before that if Settings cannot load.

AI wrote tests in a process that could already import `app`. It did not see a checkout without `.env`.
