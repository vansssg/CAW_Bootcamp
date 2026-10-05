# Module 04 BREAK Analysis

## Observed symptom from module prompt
- Intermittent extreme latency on `POST /links` for specific very long/repeating URLs.
- CPU spikes on a single core, no explicit application errors.

## Hypothesis-first investigation
Primary hypothesis:
- A pathological input-processing path (e.g., expensive string/parse operation) is triggered by crafted long URLs.

## Fastest tool checks run

1) URL parsing microbenchmark (runtime tool check)
- Command executed (Python one-liner) to benchmark `urllib.parse.urlparse` on a very long repeating URL (~200k+ chars), 50 iterations.
- Output:
  - `URLPARSE_MS_MIN 0.007`
  - `URLPARSE_MS_P95 0.012`
  - `URLPARSE_MS_MAX 0.461`

2) String sanitization microbenchmark (runtime tool check)
- Command executed to benchmark newline/carriage-return sanitization via chained `.replace(...)` on oversized string input.
- Output:
  - `SANITIZE_MS 0.002`

## What this proves
- The two directly testable candidate operations in current code (`urlparse`, log sanitization replace chain) do not explain 47-60s CPU-bound requests under this environment.

## Limitation
- Full request-level profiler trace for real `POST /links` requests remained unavailable because service dependencies were not reachable (startup remained waiting; DB connectivity unresolved), so endpoint-level CPU hotspot attribution could not be completed.

## Current conclusion
- Initial hypothesis about obvious URL parsing/string sanitization hotspot is **not supported** by measured microbench evidence.
- Additional runtime-profiler evidence is still required to isolate the true CPU hotspot once service dependencies are available.
