# AI-Augmented Engineering Module 07 CONTEXT

System review, not function review. Five things AI cannot judge, mapped to this URL shortener. Postgres/Redis/Docker still not serving.

## 1. Business logic correctness

Spec from M2/M3: only owner/admin invite. First-pass AI implemented “any authenticated principal can invite.” Code was clean; `B_IDOR_CREATE True` (HTTP 200). The model cannot know the product rule. We locked `require_team_admin` after measurement.

## 2. Security in context

`createInvitation` after auth was still wrong until the call chain checked **that** team. GET `/teams/{id}/invitations` took `principal_id` and ignored it (`BREAK_GET_LIST_SAW_HIDDEN_EMAIL True`). `update_comment` validates body then checks author — the 403 is the call-chain check, not sanitization. AI reviews the function; we review the chain.

## 3. Architectural coherence

Existing pattern: FastAPI routes, `{error:{code,message,request_id}}`, integer ids, `principal-a`/`principal-b`, in-memory like `links`. A comments agent that invented User UUIDs, `{detail}`, or Postgres NOTIFY would fork the system. We kept membership helpers and `activity.publish` shape `{type, team_id, ts, payload}`.

## 4. Data integrity under pressure

Two accepts of one invite: `acceptInvitation` has no `pending` CAS. Team delete while commenting is unimplemented (no team-delete route). WS Round-3 close-after-first dropped the second event (`BREAK_SECOND_EVENT_MISSING True`). Happy-path one client is not the system.

## 5. Compliance

Audit exists. Contract: **no email in payload**. `ITER_NO_EMAIL_IN_PAYLOAD True`, `AGENT3_AUDIT_EMAIL_LEAK False`. `emit_log` redacts emails to `[REDACTED_EMAIL]`; first-pass `print(..., email=)` did not. Tutorial audit logs are not our PII rule.
