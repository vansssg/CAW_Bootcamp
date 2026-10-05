# AI-Augmented Engineering Module 07 REFLECT

DECIDE was **B (AI-assisted hybrid)**. BREAK was the consequence: the scanner saw `require_team_member` on GET list and `require_team_admin` on POST invite and marked both authorized. It did not ask whether the check was the *right* permission, or whether list tokens + duplicate pending invites + accept overwrite compose. Human critical path caught unconstrained `role=owner` in BUILD; the remaining composition waited until BREAK.

## Numbers

| Sev | Count | Items |
|-----|-------|--------|
| Critical | 3 | Unconstrained invite `role` (owner/superadmin); accept overwrites membership; GET list returns invite tokens to any member |
| High | 2 | Duplicate pending email allowed; accept has no pending uniqueness/CAS |
| Medium | 2 | GET audit is any member; `createInvitation` camelCase vs `create_link` |
| Low | 2 | No owner-role 400 test until VERIFY; `require_team_admin` 403 still says “team invitation” on PUT |

Architecture deviations: error envelope stayed `{error:{code,message,request_id}}` (good). Copy-paste 403 on the admin helper **matters** for consumers. CamelCase names are cosmetic.

Privilege escalation: **caught analog in Step 3** (`SCAN_PRIVILEGE_ESCALATION True` on invite.role). PUT was 404 so the lesson curl was not the path. **Missed the composition until BREAK** (`BREAK_VIEWER_PROMOTED True`). Process hole: checked each control, not how they combine.

## Why the AI missed it

It was told to protect team routes. It added membership checks. “Is the user a team member? Yes. Proceed.” It does not infer that a viewer must not mint a higher role. Privilege is purpose, not presence of a function.

If Module 04’s invite prompt had said: only admin/owner create; role enum member/viewer; one pending email; list omits tokens; accept 409 if already a member; no self role-write — the generator would have had less room. Nobody said “only admins change roles,” so it did not.

Auth chain for PUT: `require_api_key` → `require_team_admin` → self-id 403 → enum → admin cannot set owner → write `memberships` → `member.updated`. Failures: wrong permission function, missing self-check, missing enum.

Scanner caught: member cannot POST invite (403). Missed: owner invite 200, GET tokens, duplicate pending, accept overwrite.

## Checklist add

- [ ] Permission checks verify the RIGHT permission, not ANY
- [ ] Role enum validated
- [ ] Self-modification blocked on role writes
- [ ] Cross-team 403/404 on every resource
- [ ] Response shape: no secrets/tokens on list
- [ ] Unique pending invite per team+email
- [ ] Accept does not overwrite an existing membership

## Knowledge

1. Problem: AI-generated auth is “a check exists,” not “the check matches the privilege.” Findings compose.
2. Biggest decision: B hybrid — spend the human hour on role writes and call-chain auth, not file-18 skim. VERIFY allowlist was necessary; BREAK showed it was not sufficient.
3. Proof: `FIX_THIRTEEN_ALL True`; after fix `BREAK_VIEWER_PROMOTED False`; `V_CROSS_ALL_DENIED True`; `V_MODULE09_EXIT 0`.

Mini task: `python -m app.scripts.module07_fix` → thirteen PUT cases OK; viewer stays viewer.

Risk: no single continuous journey (create→invite→accept→PUT role→comment→audit) in one process; GET audit still any member. Mitigation: Module 08 E2E; keep audit member-readable documented or gate later.

Postgres/Redis/Docker not claimed.
