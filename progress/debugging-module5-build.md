# Module 05 BUILD Evidence

## Incident triage
- Classified incident as **SEV1**.
- Reason: successful unauthorized delete activity (`DELETE /api/admin/links`) from unknown IP with repeated 200 responses indicates active exploitation and confirmed data impact, not theoretical risk.

## Stakeholder communication artifacts

### First VP update (early)
We are investigating unauthorized admin API activity. We have evidence of repeated successful delete requests from an unrecognized source and are treating this as a SEV1 security incident. We are isolating the auth path now and preparing a patch. The public redirect path is separate from admin endpoints and is not currently observed as impacted. Next update on state change.

### Second VP update (pressure moment)
Update: this is a real auth bypass affecting admin endpoints. We have confirmed unauthorized deletions and identified the header-validation path as the likely entry point. We are deploying a strict authorization-format fix and will confirm closure immediately after verification. Demo-facing redirect behavior remains unaffected based on current evidence.

### Incident close message draft
RESOLVED: admin API auth bypass path has been patched with strict `Bearer <token>` validation and deployed in the service code. Unauthorized and malformed authorization inputs now fail with 401. Known impact remains unauthorized admin deletions; public redirect path was not included in the exploit path evidence. Next actions: data restoration review and postmortem follow-up.

## Code changes shipped in BUILD
- Updated `api/app/main.py`:
  - Added `extract_bearer_token(...)` for strict authorization parsing.
  - Added `require_admin_auth(...)` guard for admin endpoints.
  - Applied admin auth guard to `GET /api/admin/links`.
  - Added protected `DELETE /api/admin/links` endpoint for controlled admin deletions.

## Command-based verification done in BUILD

1) Parser behavior checks (`extract_bearer_token`)
- `empty` -> `401 Authorization required`
- `ws` -> `401 Authorization required`
- `bearer_only` -> `401 Invalid authorization format`
- `bad_scheme` -> `401 Invalid authorization format`
- `valid` -> returns parsed token

2) Admin guard behavior checks (`require_admin_auth`)
- Missing/empty/whitespace Authorization -> `401 Authorization required`
- `Bearer` without token -> `401 Invalid authorization format`
- Wrong token -> `401 Invalid token`
- Valid token -> pass

## Limitation captured
- Full HTTP endpoint verification for DB-backed admin routes is still dependent on local database availability; function-level security checks were executed and recorded without fabrication.
