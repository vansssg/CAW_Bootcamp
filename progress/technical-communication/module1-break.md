# Module 1 BREAK — communication failure on a technically defensible review

The reviewer is not wrong that `d`/`cnt`/`cnt2` are unclear, that `range(len(users))` is clumsy, that the health nest is hard to follow, or that a dataclass is a reasonable alternative. The failure is communication: intent (improve the code) vs impact (author picks Option B — defensive, dreads the next PR).

## 1. Tone — charged phrases (count: 8)

Underlined:

1. “I stopped reading at the variable names.” — contempt; review abandoned
2. “d? cnt? cnt2?” — mockery
3. “Are we writing code in 1995?” — sarcasm
4. “have you never heard of iterating directly over a list?” — condescension
5. “This is Python 101.” — status put-down
6. “The nested if/else at the bottom is a mess.” — judgment, not description
7. “Refactor the whole thing.” — sweep, no target
8. “This is not how we do things.” — gatekeeping / fake “we”

## 2. Actionability

| Comment | Does the author know the next edit? |
|---------|-------------------------------------|
| Variable names | No — not told what to rename to |
| range(len) | Partially — “iterate the list” but no snippet |
| Nested if | No — “refactor the whole thing” is not a design |
| Dictionary | No — “just make a dataclass” with no fields or why |

## 3. Missing suggestions

Zero concrete alternatives. Zero code examples. Zero “consider X.” Every sentence is “this is bad.”

## 4. Missing the critical bug

`total_age / cnt` ZeroDivisionError is never mentioned. Neither is the mixed-average (all ages / active count). Style that annoyed the reviewer crowded out the production crash. After this review, the author could rename `cnt` and still ship a job that dies on an all-inactive day.

## 5. Nothing positive

No mention of: no side effects, input not mutated, docstring, `health` as a real business concept. Message received: everything you did is wrong.

## 6. The “we” problem

“This is not how we do things” treats a dict-vs-dataclass preference as a team law without a reason (typed fields, fewer key typos). That is authority, not engineering.

## Core question

I would pick **B**: feel attacked, push back, dread the next PR. Hostile tone + missed crash = worse code and a worse relationship.
