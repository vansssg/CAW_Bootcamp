# Module 2 VERIFY

## Critical path (hard edges only)

**W2 Listings (3d) → W4 Slots (3d) → W6 Booking (3d) → W11 Cancel contract (1d) → W12 Refund+admin (3d)**

1. Chain named above (BLOCKED policy sits on it so we do not code two refund systems).
2. **5 levels** (five boxes).
3. **13 focused days** minimum on that chain, regardless of headcount. Parallel W1/W5/W7/W9/W10 cannot shrink those 13 days.

Alt chain W2→W4→W6→W8 is 12d / 4 levels — shorter than W11+W12, so cancel+admin is the floor.

## Double-time test

Double **W4 slot lock** (3d → 6d): W6, W8, W11, W12 slip. **Unaffected:** W1 Auth, W2 (already done), W5 Search (only needs listings), W7 payment iface (needs auth), W3 onboarding. Overall timeline **does** change (+3d). Plan is not fully serial: search can still finish.

## Red flags

1. **Not a flat auth-root:** W2 listings starts with no auth edge. Data model does not wait on login.
2. **Not fully serial:** W5 ∥ W4 after listings; W1 ∥ W2 at start; W7 beside slot work.
3. **Not zero deps:** search needs listings; booking needs users+listings+slots; pay impl needs booking.

## Trace “user completes a booking”

Zero → W1 Auth + W2 Listings → W4 Slots → W6 Booking. W3 onboard is soft for a seed provider.

No isolated items. First build: W1 and W2, not search (CONTEXT).
