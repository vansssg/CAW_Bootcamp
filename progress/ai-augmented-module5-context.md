# AI-Augmented Engineering Module 05 CONTEXT

No code this step. Tied to the invitation work we just reviewed.

## Surface vs structural

Surface: the approach is right; a fix leaves the rest valid. On this shortener: camelCase `createInvitation`, missing email regex, empty team name. Each patch did not force a redesign.

Structural: the approach is aimed at the wrong target. Fixing it requires ripping other parts. Example we did *not* take: driving invites off Postgres `NOTIFY` on `links` while 5432 is down — that would couple delivery to a database that is not serving.

IDOR on create looked like a “missing if” (surface). GET list leaking tokens was the same missing *kind* of check on another method. Adding `require_team_member` did not invalidate accept/email/SQL. So those were surface security holes, not a wrong architecture. Restart would have been right if we had stored invites as a field on `Link` and broadcast raw rows.

## Two-iteration rule

If quality is not converging after two targeted refinements, restart with a different approach — not the same prompt in a polluted thread. Prompts 1–3 on create/SQL/email converged. Accept IDOR was a third issue the first prompts never named; that was a new prompt, not a spiral. If we had kept layering “also fix list, also fix naming, also add UUID teams” on the interpolated-SQL function, that would have been a spiral.

## Micro-exercise

Iterate **Output B** (pub/sub stubs, architecture 4/5). Restart **Output A** (NOTIFY from INSERT, no team filter). Throwing away A’s clean naming is the sunk-cost trap. Same as keeping first-pass `persist_invitation_sql` concatenation because the rest of the file looked like `main.py`.

Postgres/Redis/Docker still not serving — not used as a reason to pick NOTIFY.
