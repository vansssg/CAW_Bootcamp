# System Design Module 05 BREAK

Hard inject: `http_exception_handler` appended `pii={X-User-Email or X-API-Key}` onto `error_detail`.

Symptom: `error_detail=Invalid API key pii=ada@example.com` on a 401. Envelope stayed `{error:{code,message,request_id}}`.
