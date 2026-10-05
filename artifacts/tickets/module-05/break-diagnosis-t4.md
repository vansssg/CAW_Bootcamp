# BREAK diagnosis — T4 POST /api/bookings

Simulated AI delivery: all T4 acceptance criteria pass; four out-of-spec failures remain.

## Problem 1 — No authentication (public POST; any `learner_id`)

1. **Missing from ticket:** Explicit auth requirement *or* an explicit temporary exception. Silence + body `learner_id` was read as “public endpoint.”
2. **Ticket vs standards:** Auth *policy* is cross-cutting (every mutating route). Slice 1 guest mode is a **ticket-level** exception and must be written, not implied.
3. **Scope impact if added:** Small text change now; full auth is T5/T6 (already planned). Add: “Slice1 exception: public POST allowed; `SLICE1_GUEST_LEARNER`; superseded by T6.”

## Problem 2 — No rate limiting

1. **Missing:** Any abuse/rate-limit requirement.
2. **Ticket vs standards:** **Cross-cutting** — belongs in project standards (e.g. `artifacts/standards/api-cross-cutting.md`), not duplicated on every ticket. Ticket must **reference** the standard.
3. **Scope impact:** Small if reference-only; large if inventing per-route limiters in T4.

## Problem 3 — Generic 500s with stack traces

1. **Missing:** Behavior for unexpected errors (timeout, pool exhaustion, malformed JSON beyond 400 path).
2. **Ticket vs standards:** **Cross-cutting** error middleware / safe error envelope. Ticket references standard; does not re-specify middleware.
3. **Scope impact:** Small (reference + “must not leak stack traces”). Implementing global handler is a separate standards ticket if absent.

## Problem 4 — No logging / audit trail

1. **Missing:** Log/audit requirements for booking create.
2. **Ticket vs standards:** **Cross-cutting** structured logging. Ticket should require one info log line *or* reference the logging standard (prefer reference + “emit booking_created with booking_id, learner_id, slot_id”).
3. **Scope impact:** Small (one structured log event); full observability stack stays out of T4.

## Rule learned
Silence ≠ standard. Cross-cutting concerns live in a shared doc; every ticket either includes them or cites the doc. Accepted exceptions (guest `learner_id`) must be explicit.
