## Module 02 VERIFY - Task 1 (Requirements Spec)

### Task executed
- Ran Task 1 agent prompt (`Requirements Spec`) against `c:\UPSK-Bootcamp` with constraints: no code changes, explicit `ASSUMPTION` marking, repository-grounded references.

### What the agent produced
- A structured Team Invitation specification with the requested five sections:
  1. Feature rules
  2. Role/permission matrix
  3. Invitation state machine
  4. Edge cases
  5. External acceptance criteria checklist
- Explicit callouts that invitation workflows and route-level auth are not currently implemented in runtime code.
- Explicit assumptions around role model, recipient identity mapping, one-active-invite uniqueness, and optional worker-driven expiration sweep.
- Repository references included (for example: `api/app/main.py`, `api/app/config.py`, `api/app/models.py`, `api/alembic/versions/6c0d96e3d69b_init_schema.py`, `worker/main.py`).

### Reproducibility check (vs prior Task 1 output)
Comparison target: `progress/module-02-invitation-requirements.md`

Verdict: **Substantially reproducible at the architecture/spec level**.

Observed consistency:
- Same five output sections and same overall structure.
- Same lifecycle model (`pending`, `accepted`, `rejected`, `expired`, `revoked`).
- Same permission intent (owner/admin invite management, recipient-only accept/reject).
- Same key edge cases (duplicate invites, already-member, expired/revoked behavior, race conditions).
- Same explicit assumption discipline and repository grounding.

Observed variation (acceptable):
- Different wording/detail density in rules and checklist items.
- Matrix labels differ slightly (e.g., actor naming and view column semantics).
- Some references and examples vary by phrasing, but not by core conclusion.

### What was clear in the prompt
- Output format was explicit and strongly constrained (five exact sections).
- Scope covered the core requirement areas (lifecycle, permissions, expiry, failure scenarios).
- Evidence/assumption rules were explicit ("cite files", "mark ASSUMPTION").
- "Do not modify code" constraint was clear and followed.

### What was underspecified
- **Canonical role taxonomy** was not fixed (owner/admin/member/viewer inferred).
- **Recipient identity model** was not fixed (email-only vs user-id vs both).
- **Allowed terminal states** included "revoked if applicable" without deciding applicability.
- **Duplicate invite behavior** did not specify conflict vs idempotent return.
- **Error contract** was not explicitly required in this prompt (status codes and payload shape left to inference).
- **Cross-file reference boundaries** were not defined, so one run referenced a prior progress artifact rather than only source-code files.

### Additional context that would improve the prompt
- Define canonical role set and permission policy explicitly.
- Define identity binding rule for invite acceptance (exact user/email matching behavior).
- Define single active-invite rule and expected API behavior on duplicate submit (`409` vs idempotent `200`).
- Require a fixed error model (`401/403/404/409/410`) and response shape.
- Restrict repository evidence to source-of-truth implementation files only (exclude prior planning artifacts).
- Provide hard defaults for invite expiry duration and boundary rule (`now >= expires_at`).
- Clarify whether invites to non-registered emails are allowed.

### Verification outcome
- Task 1 prompt is strong enough to produce consistent planning output across runs, but still leaves several business-policy choices open.
- Recommended next refinement before implementation: lock the underspecified policy decisions above into the Task 1 prompt so future outputs converge even more tightly.

### Non-code-change confirmation
- This VERIFY activity produced documentation only under `progress/`.
- No application implementation files were modified during this step.
