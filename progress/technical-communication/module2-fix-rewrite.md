# REST → GraphQL (rewrite of the BREAK memo)

We are migrating ShopStream’s public API from REST (fixed URLs, canned JSON) to GraphQL (clients ask only for the fields they need) over eight weeks. That should cut frontend API calls about 40% and delete 15 aggregation endpoints.

## Decision

Three backend engineers will work full-time. Two have never used GraphQL; they will pair and study it in weeks 1–2. REST and GraphQL will both run in the cutover.

## Why

The REST API has 47 endpoints; 15 exist because web and mobile want different JSON for the same objects. Frontend (FE — the UI users see) spends much of each sprint on those one-screen routes. Site Reliability Engineering (SRE — keeps services fast and up) saw the mobile app make several REST calls where one query could do. The Software Development Kit (SDK — libraries others use to call us) team cannot keep compatibility across so many routes.

We rejected a Backend-for-Frontend (BFF — extra translation service per app) because it is another deploy to watch. Standardizing REST shapes still leaves web and mobile wanting different plates.

## Risks

Nested queries can be slow; caching is harder than REST URLs. The backend team will track query latency daily for two weeks and will announce any slip of the eight-week date in standup.

## Next for Priya

Do not add aggregation endpoint 48. Pair on the GraphQL schema with the trio Monday.
