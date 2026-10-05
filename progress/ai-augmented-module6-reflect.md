# AI-Augmented Engineering Module 06 REFLECT

## Answers

1. Three agents: comments, mentions, audit.
2. Two integration conflicts: (a) `comment.created` on the bus with audit listener cleared → audit comment count **0**; naive path middleware would have logged resource `teams`. (b) non-author comment 403 copied invitation copy (`L1_NON_AUTHOR_UPDATE DETAIL` contained invitation).
3. Parallelism saved writing three isolated modules at once. Integration cost was one glue call (`ensure_listening`) plus a 403 string. Worth it: sequential probes (module09 + parallel exit 0) beat a silent miss. Not worth it if we had skipped the bus contract and used `/teams` prefix logging.
4. Add to every contract: **who consumes which event type**, not only who emits. `add_global_listener` is the stud. Path prefix is not a resource type.

## Decision callback (A interface-first)

A was right for this shortener: shared `require_team_member` and event shape `{type, team_id, ts, payload}`. It was not enough until the contract named the subscriber. B branch-and-merge would have given a second event emitter and a middleware that labeled comments as teams — the same GET vs POST auth split from M4.

Sequential merge: comments probe, mention glue, then audit listener. Agent-assisted merge would have dropped the listener the way M4 prompts 1–3 dropped accept IDOR.

## Knowledge

1. Parallel agents need locked connection points **and** data flow.
2. Biggest decision: A + sequential integration — outsider comment 403 stayed; the miss was emit-without-subscriber.
3. Proof: BREAK_COMMENTS_MISSING_FROM_AUDIT True then FIX_COMMENTS_IN_AUDIT True; FIX_403_NOT_INVITATION True; L3_MODULE09_EXIT 0.

Risk: next agent adds HTTP audit middleware that double-logs as `teams`. Mitigation: one bus, one listener, probe comment rows after POST.
