# AI-Augmented Engineering Module 06 DECIDE

CLI A|B. Recorded **A interface_first**. Merge: **sequential_integration** (stated in reasoning; not a third CLI letter).

## Decision 1: A interface-first

This shortener already has connection points: `require_team_admin` / `require_team_member`, activity `{type, team_id, ts, payload}` without email, 401/403/409. Parallel agents for comments/members/activity must lock those before they run.

**Tradeoff vs B branch-and-merge:** B is faster to start. On this service it would recreate M4: one agent auths POST, another ships GET without membership (`BREAK_GET_LIST_SAW_HIDDEN_EMAIL True` until FIX). Merge then exceeds the parallelism savings. Wrong interface risk is real — if comments need `parent_id` later, we version the contract and re-prompt, we do not let four User models diverge.

## Decision 2: sequential integration

Commit invitations (already probed), then activity (WS two-event probe), then comments against the same helpers. Manual merge of four trees does not fit in one head. Agent-assisted merge of AI output has the same IDOR blind spot as the generators (M4: prompts 1–3 left accept IDOR). Sequential is slower than a blob merge; each step is an ASGI probe. Postgres/Redis/Docker still not claimed.
