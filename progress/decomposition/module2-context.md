# Module 2 CONTEXT — lists are not maps

House: roof after framing; electrical and plumbing after framing, in parallel. Serialize everything and you waste calendar time. Build search before the listing model and you throw away two weeks (SkillSwap analogue: search UI before provider+category rows).

DAG = Directed Acyclic Graph: arrows one way, no cycles, boxes with edges. Recipe: dice ∥ cook rice; both before plate.

## Micro-exercise

```
        [A setup DB]
           /      \
          v        v
 [B user register] [C provider profile]
          \        /
           v      v
        [D booking]
```

Arrows: A→B, A→C, B→D, C→D.

1. **Same time:** B and C (both only need A).
2. **Longest chain (critical path):** A → B → D or A → C → D (same length: 3 boxes).
3. **If A doubles:** B, C, and D all slip. Nothing can start without the DB.

SkillSwap note from M01: U-F8 cancellation BLOCKED sits on the booking chain with D. Building a slot table that assumes both cancel systems is the search-with-no-model failure.
