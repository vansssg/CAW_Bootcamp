# Module 06 FIX — close rogue enum drift

## Which fix? (required decision)

**Pick: Option 1 — fix the rogue agent to match the original contract.**

Why not Option 2 (change contract to `available`):
- Module 05 T4 / standards already standardize on `open` \| `booked`
- `available` is ambiguous (available to whom? soft-hold?)
- Changing the contract forces T4 + any other consumer rewrites; one-agent fix is cheaper

Unix/versioned-path cases can justify Option 2; this enum case does not.

## Fix applied to Stream S2
1. Response serializer / DB check: `status IN ('open','booked')`.
2. Synonym map only as migration aid: `available`→`open` (then delete synonym path).
3. Contract test:

```python
ALLOWED = {"open", "booked"}
assert set(slot["status"] for slot in body["slots"]) <= ALLOWED
```

4. Re-run CP1 → merge `agent/t3-slots`.

## Corrected S2 sample (post-FIX)
```json
{
  "provider_id": "11111111-1111-4111-8111-111111111111",
  "slots": [
    {
      "id": "b1111111-1111-4111-8111-111111111101",
      "service_id": "a1111111-1111-4111-8111-111111111111",
      "starts_at": "2026-09-01T15:00:00Z",
      "ends_at": "2026-09-01T16:00:00Z",
      "status": "open",
      "price_cents": 5000
    }
  ]
}
```

## Production symptom if missed
Booking UI shows no Tuesday slots (filter `=== "open"`). Users say “Mike has no availability” while ops sees rows in DB. Noticed after deploy when first booker fails — often Friday merge → Monday support ticket. Root cause looks like “empty inventory,” not enum drift.

## Process hardening
CP1 shared-field diff + CI contract fixture on every parallel stream.
