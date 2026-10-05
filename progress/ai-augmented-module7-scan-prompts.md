# Hybrid first-pass scan prompts (Module 07)

Do not mark OK unless the check is the right object.

1. List every FastAPI route in `api/app/main.py`. For each: is `require_api_key` called? Which of `require_team_member` / `require_team_admin` / author match / none?
2. Grep generated files for `email=` in `publish(` payloads and audit metadata.
3. Find `role` assignments that are not in an allowlist.
4. Find hardcoded secrets, `print(` of emails, new third-party deps vs `api/requirements` / existing venv packages we added for features.
5. Human then traces: POST invite role, GET invite tokens, accept membership write, WS close code.

Scanner will say POST invite is OK because `require_team_admin` exists. Human must still try `role=owner`.
