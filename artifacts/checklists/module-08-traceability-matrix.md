# Module 08 — Requirements traceability matrix

Source: `artifacts/requirements/module-01-requirements.md`  
Statuses: **Built** | **Simplified** | **Deferred** | **Lost** | **Blocked**

| ID | Requirement (short) | Status | Where / notes |
|----|---------------------|--------|---------------|
| U-F1 | Browse by category | Simplified | T2 lists category field; no filter UI (CUT search) |
| U-F2 | View provider profiles | Simplified | List+nested service; no rich profile page |
| U-F3 | Ratings on profiles | Deferred | CUT ratings |
| U-F4 | Book time slot | Built | T3+T4 happy path Scenario 1 |
| U-F5 | Pay at booking | Deferred | Simulated pay; live Stripe CUT |
| U-F6 | Confirmation email | Deferred | On-screen confirmation only |
| U-F7 | Cancel booking | Deferred | Not in 6-day plan |
| U-F8 | Cancel refund rule | Blocked | Still PM decision Option 1/2 |
| U-Q1 | Search feels instant | Deferred | No advanced search |
| U-C1 | No double-book | Built | Scenario 3 409 + unique slot_id |
| P-F1 | Set availability | Deferred | Seed slots; provider self-service CUT |
| P-F2 | Set pricing | Simplified | Seed price_cents only |
| P-F3 | Service descriptions | Simplified | Seed titles |
| P-F4 | Cancel policy | Blocked | Tied to U-F8 |
| P-F5 | See own bookings | Deferred | Provider dashboard CUT |
| P-F6 | See earnings | Deferred | Needs pay |
| P-F7 | See reviews | Deferred | |
| P-F8 | Flag no-show | Deferred | |
| P-Q1 | Dashboard at city scale | Deferred | |
| P-C1 | Pricing autonomy limits | Deferred | |
| O-F1 | Vet providers | Deferred | Seeded approved providers |
| O-F2 | Resolve disputes | Deferred | |
| O-F3 | Escalated disputes | Deferred | |
| O-F4 | Analytics | Deferred | CUT |
| O-F5 | Payout minus commission | Deferred | |
| O-C1 | 15% commission | Deferred | Not in demo path |
| O-C2 | Few thousand users | Deferred | Not load-tested here |
| O-C3 | 5 cities expand | Simplified | city field on providers |
| O-Q1 | Observability analytics | Deferred | |
| O-Q2 | Slot conflict testable | Built | Scenario 3 |
| — | Meridian book-on-behalf | Built | M07 T4/T9 |
| — | Meridian RBAC roles | Built | M07 T12 matrix Scenarios 1/4 |

## Lost?
None unmarked — every Module 1 row has a status. Deferred/Blocked are explicit, not silent drops.

## Demo claim (honest)
Investor/Meridian demo proves: browse → open slots → role-gated book-on-behalf → conflict-safe booking. Does **not** claim payments, cancel/refund, provider supply tools, or email.
