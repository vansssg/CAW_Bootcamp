# Module 05 FIX — completeness checklist

| Check | T1 | T2 | T3 | T4 | T5 | T6 |
|-------|----|----|----|----|----|-----|
| Every status code listed | n/a (CLI) | 200/500 | 200/400/404/500 | 200/201/400/404/409/429/500 | 201/400/409/429/500 | 200/401/404/500 |
| Required vs optional fields | seed IDs fixed | none | path UUID | body allowlist + optional Idempotency-Key | email/password/display_name/role required | path UUID; POST body only slot_id |
| Exact JSON shapes | stdout JSON | yes | yes | yes | yes | yes |
| Authn/authz stated | none | none (read) | none (read) | SLICE1_GUEST_LEARNER + post-T6 self-only | public register | Bearer + owner-only |
| Unexpected errors | exit non-zero | cite standards | cite standards | 500 internal_error | cite standards | cite standards |
| Output matches next input | fixed UUIDs → T2/T3/T4 | provider ids → T3 | slot ids → T4 | booking/learner → T6 | token/user → T6 | — |

Three extra T4 assumptions closed: authorization, input allowlist, idempotency.
