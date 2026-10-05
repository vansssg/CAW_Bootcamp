# Module 2 REFLECT

## Usefulness

Yes. A new hire sees: start W1 Auth ∥ W2 Listings; do not start with search; W11 BLOCKED cancel sits before refunds; full admin is last.

## Surprise

False dep: reviews need a completed booking, not payment (W8). Critical path (5 hard hops, 13d) was longer than “auth then booking” guessed. Search is slack once listings exist.

## Cycle

First reaction: this is a loop, reordering cannot start. Did not treat it as a sort. FIX split admin into W12a minimal vs W12b full; W2 `pending`.

## Hard vs soft

Soft: notify, mock payment on refunds, seed book before vetting. Hard: listings→search, slots→booking, W11→W12.

## Decision callback (B visual + shorten)

Splitting admin added an integration contract: W12a must write the same `status` W12b reads (`pending|approved`). Shorter onboarding path, more glue. Payment iface vs impl is the other shorten.

## Knowledge

1. Core problem: a flat list cannot show must-before vs can-parallel; missed deps waste work (search with no model).
2. Biggest decision: visual DAG + split overloaded nodes. Cycle visible; critical path shortenable.
3. Evidence: `artifacts/dag-module-02.md` 14 nodes after split; cycle gone; booking path W2→W4→W6→W11→W12.

## Mini practical

VERIFY critical path named in `module2-verify.md`: Listings→Slots→Booking→Cancel contract→Refund (5 levels, 13d). Unique work IDs W1–W12b present in dag file (`pending` True, `W12a` True).

## Risk / mitigation

Risk: coding both cancel options on W12. Mitigation: W11 BLOCKED until PM picks Option 1 or 2.
