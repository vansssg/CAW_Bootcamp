# Module 05 VERIFY Evidence

## 1) Severity and reasoning
- Assigned severity: **SEV1**.
- Why: unauthorized admin DELETE requests succeeded repeatedly from unrecognized source, indicating active exploitation with confirmed data impact.
- Why not SEV2: this is beyond elevated risk; exploit execution and impact already occurred.

## 2) First stakeholder update quality check
- Provided non-technical summary, impact statement, active response status, demo-specific status, and next-update expectation.
- Included scope control: admin path affected; public redirect path not observed as impacted.

## 3) Pressure-handling check
- Did not downgrade or deny breach status under pressure.
- Explicitly avoided the unsafe statement "it is not a real breach."
- Communicated confirmed impact and ongoing remediation steps.

## 4) Alert-to-first-update timing check
- In this simulated workflow, first stakeholder update was produced immediately as part of incident response artifacting.
- No prolonged silent gap was introduced in the documented response sequence.

## 5) Verification matrix for auth bypass fix
Command-based checks executed on auth validation functions:
- Empty Authorization -> 401 Authorization required
- Whitespace Authorization -> 401 Authorization required
- Bearer without token -> 401 Invalid authorization format
- Wrong token -> 401 Invalid token
- Valid Bearer token -> pass

## Limitation
- End-to-end HTTP verification against database-backed admin routes remains dependent on local DB availability; function-level security checks were executed and recorded as real evidence.
