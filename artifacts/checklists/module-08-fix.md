# Module 08 FIX — shared booking status contract

## Immediate fix choice (evaluate 3 options)

1. Booking writes `active` — rejected (loses confirmed≠in-progress nuance later)  
2. Dashboard hardcodes `confirmed` only — weak (still private vocab)  
3. **Chosen: shared `booking_status` enum** in contract; both sides consume it; dashboard filters visible set `confirmed|completed`

## Prevention
- Shared enums in interface contracts before parallel start  
- Contract tests asserting sender status ∈ receiver allow-list  
- One glossary file owned by coordinator (Mars Orbiter / M06 lesson)

## Contract patch
Add to `artifacts/contracts/module-06-interface-contracts.md` (or new `booking-status.md`):

```
booking_status: "confirmed" | "cancelled" | "completed"
Provider dashboard query: status IN ('confirmed','completed')
```

## Verification
1. Create booking → status confirmed  
2. Dashboard list includes that id  
3. Cancel → status cancelled → disappears from active dashboard filter  

## Process
Add shared enums to pre-merge contract check (Module 08 Phase 1 checklist item 3).
