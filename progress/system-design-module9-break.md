# System Design Module 09 BREAK

Hard: flaky shared state. Removed `links.clear()` from `setUp`. The in-process OrderedDict is process-global.

- Full suite: `FAILED (failures=1)` `AssertionError: 4 != 0` on `test_url_validation_rejects_javascript`.
- Same test alone: `Ran 1 test in 0.069s OK`.

The javascript POST still 400; leftover codes from create/idor/redirect/retention made `len(links)` 4. Order-dependent, not a scheme-parser bug.
