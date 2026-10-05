# Module 06 BREAK — rogue agent catch

**Presented:** Agent S2 (T3 slots) finished; AC pass in isolation. Diffed against `module-06-interface-contracts.md` C1.

## Finding (no hints used)

**Violation type: C — Enum value mismatch** (plus related status vocabulary drift)

| Field | Contract | Rogue S2 output |
|-------|----------|-----------------|
| `slots[].status` | `"open"` \| `"booked"` | `"available"` |

Source: `artifacts/parallel/module-06-agent-output-bundle.md` Stream S2 sample.

## Why tests still passed
Agent S2 unit tests asserted `status in response` and HTTP 200 only — they never asserted membership in the **contract enum**. Isolation green ≠ integration green.

## Blast radius
- T4 / frontend filters `status === "open"` → empty list or never-bookable slots
- Downstream booking never sees a bookable slot even though S2 “works”

## Not chosen (checked, clean)
- Datetimes: still ISO-8601 `Z` strings (not Unix) — Violation A absent
- Path: still `/api/providers/{id}/slots` — Violation B absent  
- IDs: still UUID strings — Violation D absent

## Coordinator action
Block merge of `agent/t3-slots`. Require remap `available`→`open` (and any `unavailable`/`taken`→`booked`) before CP2.
