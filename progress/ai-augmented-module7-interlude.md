# Interlude — SolarWinds (after M7)

## Flaws that look right

Yes. GET `/teams/{id}/invitations` looked correct: API key required, `require_team_member` present, 200 for members. A scanner marked it authorized. The flaw was the response shape (raw invite tokens) plus accept overwrite plus duplicate pending emails. Each piece followed conventions. The exploit was a sequence, not a function that “looked wrong.”

How to find it: do not only ask “is there an auth function?” Ask “what can this principal *write* after this read?” Cross-team 403 is necessary and insufficient. Probe sequences: two pending invites, list as viewer, second accept. Unicode/edge-role strings (`superadmin`) belong in the same pass.

## Implicit trust

In this workflow I trusted “membership middleware present ⇒ authorized” the same way Orion customers trusted a signed update. I have not verified the model’s training data or the provider’s handling. I have verified ASGI probes on this repo. I have not verified Docker/Postgres/Redis — they are down — so I do not treat a green scan as a green pipeline.

The build system analog here is `module09` plus targeted probes. They can pass while a composed privilege write remains, exactly as checksums passed on a poisoned binary. The mitigation is a composition pass and an E2E journey in Module 08, not more pattern-matching.
