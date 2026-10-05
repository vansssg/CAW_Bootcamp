# Module 1 VERIFY — pressure-test of code-review.md

## 1. Merge test

If the author applied only the Required Changes:

- Comment 1 adds `if cnt == 0` (or None) so `total_age / cnt` cannot raise.
- Comment 2 either sums active ages only or divides by total users.

The ZeroDivisionError is named on the exact line (`d["average_account_age"] = total_age / cnt`). The mixed-numerator bug is also named. Merge after those two would not crash and would not silently report 100 as the “active” average for ages 10 and 90.

## 2. Actionability test

Most actionable: blocker 1 — copy-pasteable `if cnt == 0` snippet plus a product question (0 vs None).

Vaguest before rewrite would have been “error handling needs work.” In the saved review the weakest remaining comment is nit 5 (dict vs dataclass) by design: it is a preference, so it should not prescribe a type. Difference: blockers name the line, the failure, and a patch; the nit names a tradeoff and explicitly says do not block.

## 3. Motivation test

Read-aloud: strengths lead; “Request changes” is about two numbers, not the author; no “why would you” / “obviously crash.” I would feel informed, not attacked. I would still push back on flattening `health` if I were in a hurry — that is labeled should-fix, so pushback is allowed.

## 4. Priority test

Labels: `[blocker]` / `[should-fix]` / `[nit / preference, not a bug]`. Final verdict says request-changes is only the two correctness issues; renames are welcome but not required.

## Red-flag scan

| Flag | Present? |
|------|----------|
| Bare LGTM | No — verdict is Request changes with reasons |
| Why would you X? with no alternative | No |
| Only negatives | No — Strengths section |
| No severity | No — blocker / should-fix / nit |
