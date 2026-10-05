# Decomposition pretest

## Part A — setup (ran locally)

- OS/shell: Windows 10 (build 26200) via Git Bash (`MINGW64_NT-10.0-26200`), bash.
- node: `v24.11.1` (v18+).
- git: `git version 2.52.0.windows.1`.
- Editor: Cursor.
- Missing: none of node/git/editor. Postgres `localhost:5432` and Redis `localhost:6379` still do not serve — recorded as env constraint, not a pretest fail.

## Part B

1. **Self-rating: ok.** I can break a spec into tasks; I still miss environment dependencies (we planned Celery/Redis jobs while `localhost:6379` was down).

2. **First thing before code:** Write the goal, constraints, and one acceptance check for a vertical slice — who the user is and what “done” looks like — then list dependencies. Do not start at file 1 of 3 pages.

3. **Order:** A and B can start in parallel. C after A. D after B and C. Serial list: **A, B, C, D** (B may overlap A; D is last).

4. **Vertical slice:** One thin path that is real for a user: UI/API → logic → stored data. We built `POST /links` → store `{long_url, owner}` → `GET /r/{code}` 307. Why: it proves the contract before we build analytics, cache, or jobs.

5. **Day 3 of a 2-week sprint, core assumption changes:** Stop the current slice. Write the new assumption, what is now invalid, and a smaller slice that still ships. Do not silently extend the sprint or keep coding the old design.

6. **Plan enough to start, then adapt.** Upfront-everything dies when Redis is down; we adapted to an in-process queue with honest evidence instead of pretending Celery was up.

7. **Good enough task:** Goal, constraints, owner, dependencies, and a done-when the next person can run without a meeting (command + expected output).

8. **Shared table mid-build:** Insert a schema/migration task both depend on, order it first, and do not keep the two tasks “independent” on paper. Same lesson as Link vs ClickEvent: the shared contract is the real dependency.
