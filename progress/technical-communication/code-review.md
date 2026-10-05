# Code Review: Add user summary generation

Inline comments (DECIDE A). Severity tags: **blocker** / **should-fix** / **nit**. Cap is five comments so this is not a wall of red.

## Decision

`review_style = inline_comments`. Auth-style reviews taught me that a crash lives on one line (`total_age / cnt`); pinning that line is how the author finds it without a meeting. Opening sentence below is the one-paragraph map; numbered comments are the load-bearing pins.

Theme: the function is a clean, side-effect-free summary, but `average_account_age` is wrong when `cnt == 0` (crash) and also wrong when inactive users exist (ages are summed for everyone, then divided only by active). Please fix those two before merge. Naming and the health nest are should-fix, not blockers. Keeping a dict return is fine for this internal tool.

## Strengths

The function is self-contained: it takes `users`, returns a dict, and does not mutate the input, print, or touch a database. That is the right shape for a summary helper. The docstring exists. The `health` labels (`mature` / `growing` / `small-active` / `at-risk`) encode a real product idea, even if the nesting is hard to read.

## Required Changes (Bugs)

**1. [blocker] `d["average_account_age"] = total_age / cnt` — ZeroDivisionError when there are zero active users**

If every user is inactive (or `users` is empty after the loop), `cnt` stays 0 and this line raises. That is not a style issue; a daily report with no active accounts will take down the job.

Suggestion: decide the empty-active contract explicitly. Two options that both work:

```python
if cnt == 0:
    d["average_account_age"] = 0  # or None, if the dashboard can render null
else:
    d["average_account_age"] = total_age / cnt
```

Question if product is unclear: should “no active users” return `average_account_age: null` plus `health: "at-risk"`, or should the function return early with zeros? Either is fine; crashing is not.

**2. [blocker] Average uses all ages in the numerator and only active users in the denominator**

`total_age` is incremented in both the `active` and `else` branches, then divided by `cnt` (active only). With one active user (age 10) and one inactive (age 90), the average becomes 100, not 10. Even after the zero-division guard, the number is still wrong.

Suggestion: either (a) add age only for active users, if “average account age” means active accounts, or (b) divide by `cnt + cnt2` (total users), if it means everyone. Please pick one and name the field so the dashboard cannot misread it (`average_active_account_age_days` vs `average_account_age_days`).

## Suggestions (Readability / Style)

**3. [should-fix] Names `d`, `cnt`, `cnt2` hide which count is which**

Six months from now `cnt2` is a puzzle. Could we rename to `summary`, `active_count`, `inactive_count`, and `total_age_days`? Same for iterating `for user in users:` instead of `for i in range(len(users))` — `i` is unused.

Not a blocker; the logic is followable once you decode the names.

**4. [should-fix] Nested `health` if/else**

The four-way nest is doing real business logic, but the happy path is buried. Would a small helper or early returns be easier to test?

```python
def classify_health(active, inactive, avg_age):
    if active <= inactive:
        return "at-risk"
    if active <= 100:
        return "small-active"
    return "mature" if avg_age > 365 else "growing"
```

Question: is “more active than inactive” the right at-risk rule when totals are tiny (1 active, 0 inactive)? If yes, keep it; if not, this helper is the place to document the threshold.

**5. [nit / preference, not a bug] Dict vs dataclass**

Building `d` by key is a valid approach for a small internal tool. A dataclass or TypedDict would give named fields and fewer string-key typos, but I would not block merge on that. If we keep the dict, the two average-age bugs above still need a written contract for missing keys.

## Final Verdict

**Request changes** — two correctness issues (crash on zero active users; average mixes inactive ages into an active-only divisor). After those are fixed and the empty-active behavior is stated in the docstring, this is mergeable. Renames and flattening `health` are welcome in the same PR but not required to land the feature.

Read-aloud check: no “why would you” / “obviously crash” / “this nesting is a mess.” Every criticism is a suggestion or a question. Dict-vs-dataclass is labeled a preference so it cannot be mistaken for a blocker.
