# Module 06 VERIFY — contracts + Sarah→Mike trace

## Contract checklist (C1 / C2)

| Question | Answer (pointer) |
|----------|-----------------|
| ID type | `artifacts/contracts/module-06-interface-contracts.md` Shared types: `provider_id`, `slot_id`, `user_id`/`learner_id` = **UUID v4** |
| Error format | Same file: `{ "error": { "code", "message" } }` + C3 cites standards |
| Datetime format | Shared types: ISO-8601 UTC with **`Z`** (`2026-09-01T15:00:00Z`) |
| Produced but not consumed? | T2 nested `bio`, `category`, `city` — UI/browse fields; slots agent ignores them (OK). T2 `service.duration_minutes` not required by slots list (slots use `starts_at`/`ends_at`). |

## Divergence caught at CP1
S2 simulated output used `status: "available"`; contract requires `open` \| `booked`. Documented in `module-06-agent-output-bundle.md`. **Not identical** → blocked merge until remap.

## End-to-end: Sarah books Mike (plumbing → use SkillSwap “guitar” seed as stand-in)

Scenario mapped to our tickets (Mike = provider-1 Ava Strings seed; plumbing→guitar lesson for demo continuity with T1 UUIDs).

1. **Browse providers** — Stream S1 / T2  
   `GET /api/providers` → Sarah sees provider `11111111-1111-4111-8111-111111111111`.

2. **Show Mike’s slots** — Stream S2 / T3  
   `GET /api/providers/11111111-1111-4111-8111-111111111111/slots`  
   Expected (post-fix): slots with `status:"open"`, `starts_at` e.g. Tuesday 14:00Z.

3. **Create booking** — T4 (serial, not in parallel set; contract consumer)  
   Request (Slice1 guest or later auth):
   ```json
   { "learner_id": "<Sarah UUID>", "slot_id": "b1111111-1111-4111-8111-111111111101" }
   ```
   Expect 201 `status:"confirmed"` OR 409 `slot_unavailable` if raced.

4. **Shape match S2 → frontend → T4?**  
   Frontend must send `slot_id` from S2 `slots[].id` (UUID). T4 does **not** re-fetch availability shape for create — it needs `slot_id` + learner. S2 `status` must be `open` or T4’s open-check fails. **Pre-fix `available` breaks this match.**

5. **Race: slot booked between view and confirm**  
   Handled by **T4** (booking agent): conditional `UPDATE ... WHERE status='open'` + unique `bookings.slot_id` → **409 `slot_unavailable`**. Covered in Module 05 T4 contract / Module 06 C1 sync notes. Availability list agent (S2) is not the race authority.

## Red-flag self-check
- Contracts written **before** simulated launch (execution plan step 2).  
- Contracts customized (SkillSwap T2/T3/T5 + seed UUIDs), not bare template.  
- Divergence **noticed** at CP1 (`available` ≠ `open`).
