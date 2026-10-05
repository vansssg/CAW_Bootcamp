# Module 07 Chunk 3 — follow postgres-unreachable.md as a stranger

Did **not** run `docker stop postgres`: daemon is down; 5432 already times out. That is the failure the runbook is for.

## Commands as written → actual

| Step | Documented | Actual | Fix applied |
|---|---|---|---|
| `/live` | 200 `{"ok": true}` | `LIVE 200 0.052 {"ok":true}` | Dropped space in JSON; recorded 0.052s |
| `/ready` once | 503 ~4s or 4ms if open | `READY1 503 4.082` envelope `service_unavailable` | Quoted real JSON; **removed** “4ms after one probe” (READY2 still 4.073s, breaker still closed) |
| `docker ps` | empty or generic daemon error | `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` | Pasted exact error |
| TCP 5432 | Timeout or refused | `TimeoutError timed out` | Listed TimeoutError first |
| `docker compose up` | start container | **not run** — daemon down | Escalation already said stop; did not fake a start |

**Fixes needed on first test: 5** (postgres-unreachable.md). Those are 3 AM footguns.

VERIFY scan also inlined copy-paste commands into high-error-rate.md and high-latency.md (they previously said “same commands as Postgres runbook”).

Honest bound: `/ready` 200 was never observed here. Verification of “DB started” remains unproven until Docker works.
