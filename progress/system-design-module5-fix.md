# System Design Module 05 FIX

Error is created in `require_api_key` as HTTPException 401. `http_exception_handler` maps it to `{error:{code,message,request_id}}` and logs `error_detail` without headers.

The inject appended `pii={email or api key}` onto that log field. Removed it. `redact_secrets` still strips JWT/API keys, `DO_NOT_LOG_ME_123`, and email-shaped strings if they appear.

Regression: `FIX_PII_IN_LOGS False`; envelope verify script still green.
