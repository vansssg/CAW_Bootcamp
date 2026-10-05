## Module 02 FIX - Task 1 Prompt/Process Improvement

### 1) What was missing

From `progress/module-02-task1-verify.md`, the Task 1 prompt was strong but left several policy choices open:

- Canonical role taxonomy was not fixed.
- Recipient identity binding model was not fixed (email vs user id vs both).
- Revoked-state applicability was optional ("if applicable"), not decided.
- Duplicate active-invite behavior was ambiguous (`409` conflict vs idempotent success).
- Error contract was not fixed (status codes and payload shape).
- Evidence-reference boundaries were not fixed (agent could cite prior planning docs instead of source-of-truth implementation files).
- Expiry defaults were not fixed (duration and boundary rule needed explicit contract).
- Non-registered recipient policy was not fixed.

---

### 2) What was changed in the prompt/process

## Task 1 Prompt v2 (Requirements Spec)

Use this exact prompt for future Task 1 runs:

Create a structured specification for the Team Invitation feature in this repository.

Scope:
- Define invitation lifecycle states.
- Define who can send invites, who can accept/reject, and role-based permission boundaries.
- Define expiry behavior and invalidation rules.
- Define success/failure scenarios and edge cases.

Policy decisions to treat as fixed for this task:
- Canonical team roles: `owner`, `admin`, `member`, `viewer`.
- Invitation states: `pending`, `accepted`, `rejected`, `expired`, `revoked` (revoked is required, not optional).
- Recipient identity rule: invite is bound to recipient email; accept/reject requires authenticated principal email match (case-insensitive normalized match).
- Active invite uniqueness: max one `pending` invite per `(team_id, recipient_email_normalized)`.
- Duplicate create behavior: return `409 Conflict` when a pending invite already exists.
- Error model contract:
  - `401` unauthenticated
  - `403` forbidden
  - `404` not found
  - `409` conflict / invalid-state
  - `410` expired invite
  - Error payload shape: `{ "detail": "<message>" }`
- Expiry contract:
  - default duration: 7 days from creation
  - boundary rule: `now >= expires_at` means expired and non-actionable.
- Non-registered recipients: allowed by email invite; membership is created only after recipient authenticates and accepts.

Repository evidence rules:
- Cite only source-of-truth implementation files from repository code/config/migrations.
- Do not use prior `progress/` artifacts as evidence.
- If evidence is unavailable, mark `ASSUMPTION` explicitly.

Constraints:
- Do not modify code.
- Base conclusions on repository patterns and current architecture.
- Mark unknown facts as `ASSUMPTION` (no silent guessing).

Output format:
1) Feature rules
2) Role/permission matrix
3) Invitation state machine
4) Edge cases
5) External acceptance criteria checklist
6) Assumption trace (explicit)

Return only markdown content.

## Process updates (pre-run + post-run)

- **Pre-run policy lock:** Attach the fixed policy block above before each Task 1 execution.
- **Evidence boundary check:** Require at least 5 references to source files and zero references to `progress/` docs.
- **Determinism check:** Re-run prompt once and compare for structural parity (same six sections + same fixed policies).
- **Underspecification gate:** If any fixed policy reappears as `ASSUMPTION`, mark run as failed and revise prompt.

---

### 3) Why this improves AI output quality

- Removes ambiguous policy choices, reducing agent guesswork and run-to-run drift.
- Converts implicit expectations into explicit contracts (roles, states, errors, identity, expiry, duplicates).
- Increases reproducibility by fixing both output structure and business rules.
- Improves reviewability because every output is evaluated against the same deterministic checklist.
- Prevents circular evidence by forcing grounding in source-of-truth files rather than prior planning artifacts.
- Preserves safety: unknown repository facts are still surfaced transparently via explicit `ASSUMPTION` tags.

---

### Non-code-change confirmation

- This FIX step updated process documentation only at `progress/module-02-task1-fix.md`.
- No application implementation files were modified.
