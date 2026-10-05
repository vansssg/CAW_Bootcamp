# AI-Augmented Engineering Module 06 BREAK

Comments HTTP 200 and `comment.created` on the bus. Audit has **zero** comment rows when global listeners are cleared.

That is the contract hole: Agent 1 emits; Agent 3 was specified as HTTP middleware. A naive path split on `/teams/1/comments` yields resource `teams`, not `comment`. Events go to the void without `add_global_listener`.

Measured: BREAK_BUS_HAS_COMMENT_CREATED True; BREAK_AUDIT_COMMENT_COUNT 0; BREAK_NAIVE_MIDDLEWARE_RESOURCE teams.
