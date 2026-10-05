# System Design Module 05 REFLECT

Strategy: fail-fast (A). Implication: bad input and unhandled errors surface as 4xx/5xx envelopes immediately; we do not return partial link JSON.

Logging rule: never copy request headers into `error_detail`; redact secrets and email-shaped strings.

Knowledge:
1. Clients get a safe, stable error; engineers get request_id + stack in logs.
2. Fail-fast vs graceful: a wrong redirect is worse than 500/404.
3. module05_error_verify.py 400/422/500 + SENTINEL_IN_LOGS False.

Risk: logging exception messages that contain connection strings. Mitigation: redact_secrets on every emit_log field; generic 500 body.
