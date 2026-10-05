# Technical Explanation: REST-to-GraphQL Migration

We are migrating ShopStream’s public API from REST to GraphQL over eight weeks so web and mobile can ask for exactly the fields they need. That cut should drop frontend API calls by about 40% and let us delete 15 one-screen aggregation endpoints.

## Decision Summary

**Decision:** run GraphQL beside REST for eight weeks, then retire the 15 aggregation endpoints. Three backend engineers are full-time on it; two of them are learning GraphQL on the job.

REST is our current style of API: the server owns a fixed menu of URLs (endpoints — one URL, one canned response). GraphQL is a query language for APIs: the client writes a shopping list of fields and gets only those fields (buffet, not dish #7 with an unwanted side salad).

Priya: you were not in the room six months ago. The rest of this page is why we did it, what can go wrong, and what you do Monday.

## Why We Chose This

Frontend spends about 30% of each sprint building aggregation endpoints — REST routes that stitch several services into the shape of one screen. We have 47 REST endpoints today; 15 exist only because mobile wants a different JSON shape than web for the same page.

A Backend-for-Frontend (BFF — a extra translation service per app) would add another thing to deploy and watch. Standardizing REST shapes would still leave web and mobile wanting different plates. GraphQL lets each client pick its own plate from one schema.

Expected outcomes:

- ~40% fewer frontend API calls (one GraphQL query replaces several REST round-trips)
- Delete the 15 single-purpose aggregation endpoints
- Faster mobile features after those endpoints are gone

## Risks and Mitigations

**Learning curve.** Two of three engineers have never used GraphQL. Mitigation: pair programming and a shared schema review (the typed menu of fields a client may request) before any resolver (the function that fetches one field) ships. Priya joins that pairing, not a solo firehose.

**Unpredictable query cost.** A client can ask for deeply nested data and stall the database. Mitigation: query-depth limits and a list of allowed operations in production until we have metrics.

**Caching is harder.** REST URLs are easy to cache (same path, same body). GraphQL usually POSTs a query string, so a CDN cannot key on the URL alone. Mitigation: keep REST caching for hot GETs during dual-run; add persisted queries (named, allow-listed documents) before we turn REST off.

## What This Means for Priya

You are not expected to know GraphQL on day one. You are expected to help keep the dual-run honest: every new screen should hit GraphQL, not a new aggregation endpoint.

You will own (with a named buddy from the three) one slice of the schema — likely a product or cart type — including the resolver and a test that the old REST shape still matches during dual-run.

Talk to the migration trio before adding any new REST route. If a PM asks for “one more aggregation endpoint,” the answer is a GraphQL field, not endpoint 48.

## Next Steps

| When | Who | Done when |
|------|-----|-----------|
| Monday standup | Priya + migration trio | Priya has a schema slice and a buddy name |
| Week 1 | Priya | First query against the dual-run GraphQL endpoint returns the same fields as the REST screen she was assigned |
| Weeks 2–8 | Backend team | Dual-run stays up; no new aggregation endpoints |
| After week 8 | Backend team | 15 aggregation endpoints deprecated; GraphQL is the public path |

Do not wait for a “let us know if you have questions.” If the buddy is unclear Monday, ping the migration trio in `#shopstream-api` before writing REST.
