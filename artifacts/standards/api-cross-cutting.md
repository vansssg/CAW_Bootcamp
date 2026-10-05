# SkillSwap API cross-cutting standards

Every ticket that adds or changes an HTTP route **must** cite this file under Constraints, or explicitly document a dated exception.

## Authentication
- Mutating routes (`POST`/`PUT`/`PATCH`/`DELETE`) require `Authorization: Bearer <token>` unless the ticket states a named exception (e.g. `SLICE1_GUEST_LEARNER`).
- Identity for ownership fields comes from the session, never from a client-supplied user id, once auth exists.

## Rate limiting
- Public and authenticated write endpoints: default **60 requests / minute / IP** (token bucket).
- Return `429` with `{ "error": { "code": "rate_limited", "message": "Too many requests" } }`.

## Error handling
- All errors use `{ "error": { "code": "string", "message": "string" } }`.
- Unexpected failures → `500` with `code: "internal_error"` and a **generic** message.
- **Never** return stack traces, SQL text, or filesystem paths in responses.

## Logging
- Structured logs (JSON): at minimum `event`, `request_id`, `route`, `status_code`.
- Booking create must emit `event=booking_created` with `booking_id`, `learner_id`, `slot_id` (no secrets/passwords).
- Do not log full Authorization headers or raw passwords.
