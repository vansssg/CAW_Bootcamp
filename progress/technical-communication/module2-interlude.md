# Interlude — Mars Climate Orbiter (1999)

23 Sep 1999: Mars Climate Orbiter never reappeared after orbit insertion. Lockheed thruster software reported impulse in pound-force seconds; JPL navigation expected newton-seconds (~4.45×). The interface spec said “total impulse” and omitted units. Errors accumulated over 416 million miles; arrival was ~170 km too low (~57 km vs 226 km planned). $327M lost. Both teams were competent; the gap was the interface.

Fix that would have been enough: **“Total impulse (newton-seconds).”** Four words. Verification lesson: producer and consumer must each show what they think the spec means and compare — not “did you read it?”

## 1. Implicit assumptions in technical-explanation.md

Counted and then made explicit where cheap:

| Assumption I almost left implicit | Four-word-class fix |
|---|---|
| “Aggregation endpoint” is obvious | BUILD already defined: REST routes that stitch several services into one screen |
| GraphQL “schema” / “resolver” | VERIFY patch: typed menu of fields; function that fetches one field |
| Dual-run means REST stays until GraphQL matches | Stated: both run eight weeks |
| 40% is a forecast not a measurement | Said “should” / “expected” |
| `#shopstream-api` exists and Priya has access | Named the channel; still assumes Slack |
| “Buddy” is a named engineer from the trio | Table: Priya + migration trio Monday |
| Query-depth limits will be enforced in prod | Risks section — still does not name the numeric depth |

Knight/Mars lesson: the leftover risk is **query depth** without a number (like impulse without units).

## 2. Interfaces I have not dual-verified

On this bootcamp API: `not_owner_status=404` vs 403. One team reads “not found,” another reads “forbidden.” We chose 404 in System Design M04 and proved it with `module04_auth_verify.py` — that is the “show me what you think it means” check. Still unverified with a live second consumer: Redis cache key `redir:{code}` TTL 60s vs a worker that might assume infinite. Postgres is down so we never compared producer vs consumer on `DATABASE_URL`.

## 3. Which trivial clarifications are worth it

Worth it when two teams meet at a number: units, status codes, TTL seconds, hash vs raw IP. Cheap like four words; expensive like $327M or a 401/404 IDOR debate.

Clarification I was putting off: **GraphQL query max depth** in the Priya doc. Adding “max depth 5 in production” is the impulse-unit line. Noted as a leftover; not fabricated as already in the shipped file.

## Connecting question

Four words missing from my BUILD doc: **“max query depth 5.”** Same class as “total impulse (newton-seconds).”
