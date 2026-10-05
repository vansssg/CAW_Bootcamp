# SkillSwap DAG — Module 02

`dag_representation = visual_graph`  
`critical_path_strategy = actively_shorten` (payment **interface** split from **implementation**; cancel **policy contract** split from **refund job**)

Source: `artifacts/requirements/module-01-requirements.md` (25 rows). U-F8/P-F4 remain **BLOCKED**.

## 3a — Work items (12)

| ID | Work item | Covers | Size |
|----|-----------|--------|------|
| W1 | Auth | learner/provider identity (silence-pass; required so booking compiles) | 2d |
| W2 | Listings data model | U-F2, P-F2, P-F3, categories U-F1, city field O-C3 | 2–3d |
| W3 | Provider onboarding | O-F1 vet/approve | 2d |
| W4 | Availability + slot lock | P-F1, U-C1, O-Q2 | 2–3d |
| W5 | Search & browse | U-F1, U-Q1 | 2–3d |
| W6 | Booking flow | U-F4 | 2–3d |
| W7 | Payment **interface** | hold-vs-capture + 15% split contract (O-C1, O-F5) | 1d |
| W8 | Payment **implementation** | U-F5, P-F6 | 2–3d |
| W9 | Reviews + no-show flag | U-F3, P-F7, P-F8 | 2d |
| W10 | Notifications | U-F6 | 1–2d |
| W11 | Cancellation **policy contract** | U-F8/P-F4 BLOCKED — Option 1 or 2 clocks only | 1d |
| W12 | Cancellation **refund flow** + admin/disputes/analytics | U-F7, O-F2, O-F3, O-F4, O-Q1, P-Q1 | 3d |

Check: every M01 row maps to a W*. Auth was a silence; promoting it here so the DAG cannot skip identity.

## 3b–3c — Visual DAG (H = hard, S = soft)

```
 [W1 Auth]                 [W2 Listings]
    |  \                    /  |   \
    |   \                  /   |    \
    |    H                H    H     H
    |     \              /     |      \
    |      v            v      v       v
    |    [W3 Onboard] [W4 Slots] [W5 Search]
    |         |           |
    |         S           H
    |         v           v
    |              [W6 Booking]
    |               /   |    \
    H              H    H     S
    |             /     |      \
    v            v      v       v
 [W7 Pay iface] [W8 Pay] [W11 Cancel contract] [W10 Notify]
         \         |              |
          H        H              H
           \       |              |
            v      v              v
              [W12 Refund+admin]     [W9 Reviews]
                    ^                     |
                    |                     |
                    +---- S (earnings) ---+
```

Edges (from → to):

| From | To | H/S | Why |
|------|----|-----|-----|
| W1 | W3 | H | Cannot vet a provider with no identity |
| W1 | W6 | H | Booking needs who |
| W1 | W7 | H | Payment iface needs payer id |
| W1 | W9 | H | Reviewer identity |
| W2 | W3 | S | Onboarding can start with a stub profile schema |
| W2 | W4 | H | Slots hang off a listing |
| W2 | W5 | H | Search cannot query unstructured air (CONTEXT search-without-model) |
| W2 | W6 | H | Book a listing that exists |
| W4 | W6 | H | Pick a locked slot |
| W3 | W6 | S | Can book a seed provider before full vetting in a test env |
| W6 | W8 | H | Charge a real booking id |
| W6 | W10 | S | Booking works without email |
| W6 | W11 | H | Policy contract is about a booking timestamp vs appointment |
| W6 | W9 | H | Review needs a completed booking — **not** W8 (false dep) |
| W7 | W8 | H | Implementation fills the iface |
| W7 | W12 | S | Refunds can mock the iface |
| W11 | W12 | H | Refund job cannot code both Option 1 and Option 2 |
| W8 | W12 | S | Earnings display after refund; stub ok |

No cycles. If W12 → W6 appeared, that would be a cycle (refunds creating bookings).

## Starting points (no incoming)

- **W1 Auth**
- **W2 Listings**
- **W11** has incoming from W6 — not a start.
- **W7** has incoming from W1.

Starts: **W1, W2**. (W7 waits on W1 only — can start the same day as listings.)

## Endpoints (no outgoing)

- **W5 Search**
- **W9 Reviews**
- **W10 Notifications**
- **W12 Refund+admin**

## Critical path (after shorten)

Without split: W1/W2 → W4 → W6 → W8 → W12 (five deep if serialized).

With interface split: W1 → W7 runs **beside** W2→W4→W6. W11 (policy contract) is a one-day document that **blocks W12** until the PM picks Option 1 or 2 — it does not block W4/W5. That is actively_shorten: do not wait for a finished booking UI to write the refund clock.

Floor duration ≈ max(W1+W7, W2+W4+W6) then W12. Search (W5) is off the critical path (slack) once listings exist — do not staff it first (CONTEXT failure).
