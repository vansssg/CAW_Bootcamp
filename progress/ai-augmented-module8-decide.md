# AI-Augmented Engineering Module 08 DECIDE

**B production_grade.**

This is not a 10-user internal tool. Other skills already depend on this shortener. Highest-probability failure if we ship now: CI stays green while a PUT/invite privilege regression lands, because `.github/workflows/ci.yml` only runs `test_query_columns.py` and `module09_test_suite.py`. `FIX_THIRTEEN_ALL` is local only.

Five tests that must gate (not five happy paths):
1. Viewer PUT self to admin → 403
2. Owner invite `role=owner` → 400
3. Cross-team comment/invite/audit/list → 403
4. Accept does not overwrite an existing membership (409)
5. module09 links suite still exit 0

Ship: those gates in CI, a short team RBAC doc (how to add a role), rollback note already in ci.yml. Defer: live Docker/Postgres/Redis (not serving here), `/ready` 200 against a real DB, every comment edge case.

A (ship and iterate) would merge with a pipeline that cannot see M07. That is the restaurant without the fire inspection: the kitchen works on this laptop.
