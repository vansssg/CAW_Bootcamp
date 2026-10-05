# Module 1 REFLECT

## Decision callback (chose A inline_comments)

I chose line-by-line because an auth-style crash lives on one assignment (`total_age / cnt`). BREAK showed the failure mode of careless inline: every hostile comment aimed at a line (names, `range(len)`, nest, dict) and still missed the ZeroDivisionError. Granularity does not guarantee thoroughness. My BUILD/FIX comments put **Bug** on that line first and capped at five comments so style could not bury it.

Would I choose differently?
- 15-file PR: lead with a summary (must-fix list), then a few inline pins. Pure inline is death by paper cuts.
- 5-line PR: inline only; a summary would be heavier than the diff.

## 1. Review style and reasoning

Stored: `inline_comments`. Scenario was a single function with a buried crash. Inline pins the divisor. Mitigation I accepted: one theme sentence + severity tags + comment cap.

## 2. Tone vs effectiveness

Hostile review had the same name/loop/nest/dataclass observations and still would not merge the crash fix — it starts a two-day dataclass argument. Constructive review with the same bar plus the bug labeled **Bug** gets the PR merged the same day. How you say it determines whether the code actually changes.

## 3. Gatekeeping vs collaboration

Gatekeeping: “not how we do things.” Collaboration: “dict is valid; empty-active contract still needs to be explicit.” I want to practice and receive collaboration. Quality bar stays: ZeroDivisionError is still must-fix.

## Knowledge check

1. Core problem: technically correct reviews that feel like attacks (or miss the production crash while nitting names) do not improve the codebase.
2. Biggest-impact decision: putting the ZeroDivisionError first under inline review. Style without that pin ships a crashing job.
3. End-to-end evidence: `progress/technical-communication/code-review.md` Required Changes 1 names `total_age / cnt`; `module1-fix.md` rewrite labels it **Bug (must fix)** with 0/None/early-return options.

## Mini practical (VERIFY)

Rewritten comment + severity from `code-review.md`:

> **1. [blocker]** `d["average_account_age"] = total_age / cnt` — ZeroDivisionError when there are zero active users

Severity label used: `[blocker]` vs `[should-fix]` vs `[nit / preference, not a bug]`.

## Risk and mitigation

Risk: inline comments drown the crash in nits (BREAK review). Mitigation: severity labels and a must-fix section before suggestions; comment cap 3–5.
