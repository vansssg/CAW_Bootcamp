# Module 08 BREAK — provider dashboard missing new bookings

**Symptom:** Bookings create successfully; dashboard loads; new bookings absent from list.

## Trace (0 hints)
1. Create booking → DB/API shows `status: "confirmed"` (per T4).
2. Dashboard fetch filters `status == "active"` (per dashboard ticket).
3. **Mismatch:** `confirmed` ∉ dashboard filter → empty list.
4. Classification: **contract / shared enum gap**, not a defect inside either component.

## Root cause
No shared booking-status vocabulary across booking write path and provider read path (same class of bug as Module 06 `open` vs `available`).

## Note for SkillSwap demo
Provider dashboard was CUT in Module 07 — bug still valid as integration lesson for post-demo P-F5; status enum must be in shared contract before that ticket ships.
