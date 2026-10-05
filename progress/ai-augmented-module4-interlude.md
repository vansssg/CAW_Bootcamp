# Interlude — Samsung AI code leak (after M4)

What goes *in* to the model is as much a review surface as what comes *out*.

## What I would not paste

On this shortener: `DATABASE_URL` passwords, `API_KEY_A`/`API_KEY_B`, `JWT_SECRET`, live invitation tokens, raw invitee emails, customer IPs. Those already have a local analogue — `redact_secrets` turns emails into `[REDACTED_EMAIL]` in logs; a prompt should be at least that strict.

The line is policy plus instinct, not “never thought about it.” Application code that already lives in this workspace can be *read* by a local agent without me copying it into a public chat that may train on inputs. Pasting the same files into a consumer ChatGPT window is the Samsung move: the bug gets fixed, the boundary is gone.

## Middle path vs blanket ban

A total ban does not survive 11pm. People use phones. Safer controls that still let engineers ship:

- Secrets stay in env, never in the prompt or in git.
- Enterprise tenant with zero retention / no training on prompts, or a model that stays inside the company network (Samsung’s later internal tool).
- DLP / secret scanning on paste, not a warning after the fact.
- Prefer local repo-aware agents over copy-paste into a browser.

Those controls fail if the developer still pastes `.env`. The review skill from Module 04 applies inbound: treat every prompt like a PR of what leaves the building.
