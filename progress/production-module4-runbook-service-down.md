# Runbook: ServiceDown

Alert fires when Prometheus `up == 0` for 1 minute (scrape of `/metrics` failed).

1. Confirm process listen: `GET /live` should return 200 without touching Postgres.
2. If `/live` fails, restart the API process and check startup logs (`service starting`).
3. If `/live` works but scrape fails, check bind address, scrape path `/metrics`, and firewall.
4. Do not confuse this with `/ready` failure: DB timeout is readiness, not "service down".
