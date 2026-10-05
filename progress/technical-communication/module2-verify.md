# Module 2 VERIFY — three checks

## Check 1: Headline test

First sentence of `technical-explanation.md`:

> We are migrating ShopStream’s public API from REST to GraphQL over eight weeks so web and mobile can ask for exactly the fields they need.

Answers what (REST → GraphQL, eight weeks) and why I should care (exact fields). Not a buried lede. Weak counter-example (“over the past several months we have been discussing…”) is not this opening.

## Check 2: Longest paragraph

Longest body paragraphs are 2–3 sentences (`Why We Chose This` BFF/standardize paragraph; `Caching is harder`). None exceed four sentences. One-job rule holds. Next Steps is a table, not a wall.

## Check 3: Passive scan

Searched for “it was decided”, “will be completed”, “should be done”, “has been implemented”: none in the file.

Action items use a Who column: Priya, migration trio, backend team. “After those endpoints are gone” is a fact, not an ownerless to-do.

## Red flags

- Opening is the point, not background.
- REST, GraphQL, endpoint, BFF defined on first use. VERIFY found `schema` and `resolver` used later without a definition — patched in Risks: schema = typed menu of fields; resolver = function that fetches one field.
- Headings + bullets + table: scannable.
- Ending is a dated table, not “feel free to reach out.”
