# Module 03 FIX - Missing Context Trace

## 1) Violation Identified
- The original permission plan (`progress/module-03-team-invitation-permission-plan.md`) introduced a broad status-code policy (`401/403/409/422`) as if it were baseline convention, while current runtime evidence in `api/app/main.py` explicitly demonstrates `400` and `404` plus `HTTPException` -> `{"detail": ...}` envelope.

## 2) Trace to Missing Context
- Missing/under-specified context was not a file absence as much as a missing explicit constraint statement in the context package:
  - Required strict statement: error envelope must remain `{"detail":"..."}` through `HTTPException` handler in `api/app/main.py`.
  - Required grounding statement: only `400/404` are evidenced in current runtime; other status codes must be marked as assumptions for future auth/invitation implementation.

## 3) Context Fix Applied
- Added explicit, non-optional context constraints for rerun:
  - enforce `HTTPException` + `{"detail":"..."}` only.
  - forbid alternate envelopes.
  - separate evidenced status conventions (`400`, `404`) from assumption-only future codes (`401/403/409/422`).
- Re-ran Task 3 with corrected context and saved output to:
  - `progress/module-03-team-invitation-permission-plan-rerun.md`

## 4) Re-run Verification Outcome
- Re-run output now aligns with runtime error-envelope convention.
- Re-run output explicitly separates:
  - evidenced conventions (400/404 + `{"detail":"..."}`), and
  - assumption-only future auth/invitation mappings.
- This demonstrates context was the root cause; prompt intent stayed the same while output quality improved after context tightening.

## Non-code-change confirmation
- FIX step produced documentation artifacts only.
- No application implementation files were modified.
