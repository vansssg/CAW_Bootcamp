# Module 2 DECIDE

## Decision 1 — DAG representation: **B visual_graph**

A new SkillSwap developer mid-sprint needs a map, not street-by-street arrows. Adjacency lists version-control well but hide bottlenecks (auth, listings model) and parallel tracks (B∥C). ASCII/Mermaid shows fan-out and converge. Fast solo work could use a list; this pack is a team artifact chain.

`decisions.module_02.dag_representation = visual_graph`

## Decision 2 — Critical path: **B actively_shorten** (record when CLI asks)

Auth → booking → payment → commission is four sprints if left whole. Split **payment interface / refund contract** (can start after a one-page booking payload, does not wait for full booking UI) from **payment implementation**. Same for cancel: BLOCKED U-F8 must not sit behind a finished slot table — define the refund clock as an interface first.

Tradeoff: more integration points. Worth it so the six-week cancel rebuild cannot hide on the longest chain.

`decisions.module_02.critical_path_strategy = actively_shorten`
