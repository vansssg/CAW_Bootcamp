# Module 04 REFLECT

## Decision reflection
- I would keep the same DECIDE choices: manual profiling first and targeted-first scope with broad fallback.
- Manual profiling was low overhead for focused micro-checks, but it required deliberate timing and did not provide retroactive history.
- Targeted scope was efficient for testable hypotheses; broad scope remains useful when the failure surface is unknown.

## Tool-usage reflection (evidence-bound)
- Memory leak/N+1 full profiler traces were blocked by local dependency availability (service startup waited on unresolved DB connectivity), so no fabricated heap/query logs were claimed.
- BREAK analysis used measurable runtime checks to reject a false hotspot hypothesis:
  - long-URL `urlparse` benchmark did not show pathological cost.
  - oversized-string sanitization benchmark did not show pathological cost.
- FIX verification used a direct callable check proving immediate oversized-input rejection:
  - status 400 and ~0.017ms elapsed for oversized URL input.

## Bigger-picture reflection
- Example where tooling beat code reading: microbench commands falsified an intuitive hotspot hypothesis quickly; reading alone could not quantify whether URL parsing/sanitization were truly expensive.
- Tool selection order:
  - profiler first for CPU/memory saturation without explicit errors,
  - logs first for request timeline and error-path correlation,
  - reproduction script first when the failure trigger needs deterministic replay.

## Knowledge check
1. Core problem solved: identifying runtime performance bottlenecks that code reading alone can miss.
2. Biggest-impact decision: inspection scope strategy (targeted vs broad), because it controls signal-to-noise and time-to-isolation.
3. End-to-end proof available here: implemented URL length guard and verified fast malicious-input rejection with command output.

## Mini practical task (STEP 4 style proof)
- Action: verified malicious oversized URL is rejected immediately.
- Command output (captured in FIX evidence):
  - `STATUS 400`
  - `DETAIL URL is too long. Maximum length is 2048 characters.`
  - `ELAPSED_MS 0.017`

## Risk + mitigation
- Risk: unavailable runtime dependencies can hide or delay performance root-cause confirmation.
- Mitigation: maintain fallback verification layers (function-level timing checks + explicit limitation logging) and rerun full profiler/query verification once dependencies are restored.
