# Module 03 BREAK - Convention Violation Analysis

## Observed Symptom
- The `permission-plan` output proposes an expanded authorization/error status policy (`401/403/404/409/422`) that goes beyond currently demonstrated runtime status conventions.

## Hypothesis
- The permission-plan introduced generalized auth/error mappings that are reasonable in isolation but not fully anchored to the current `api/app/main.py` error-handling baseline.

## Fastest Verification Checks Run
1. Checked `progress/module-03-team-invitation-permission-plan.md` for proposed status mappings and response contract.
2. Checked `api/app/main.py` for actual `HTTPException` usage and status-code patterns.

## Evidence

From `progress/module-03-team-invitation-permission-plan.md`:
- Explicitly recommends: `401`, `403`, `404`, `409`, `422`.
- Uses mixed conflict guidance such as `409` (with fallback `400/404`) for some state paths.

From `api/app/main.py`:
- Runtime error envelope is `{"detail": ...}` via the global `HTTPException` handler.
- Observed explicit statuses in current routes are `400` and `404`.
- No existing invitation/auth routes showing established `401/403/409/422` operational behavior.

## Conclusion
- **Hypothesis confirmed.** The main divergence is in `permission-plan`: status-code policy is broader than the currently demonstrated runtime convention set.
- The output is not “wrong,” but it is partially assumption-driven relative to the current baseline and therefore needs contract tightening in FIX.

## Non-code-change confirmation
- This BREAK step produced analysis documentation only.
- No application implementation files were modified.
