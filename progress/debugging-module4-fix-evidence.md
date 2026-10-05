# Module 04 FIX Evidence

## Implemented fix
- Updated `api/app/main.py` in `create_link` to reject oversized URLs before parsing or database work.
- Added `MAX_URL_LENGTH = 2048`.
- Added guard:
  - `if len(link.long_url) > MAX_URL_LENGTH: raise HTTPException(status_code=400, ...)`

## Why this addresses the BREAK scenario
- The reported CPU spike is input-shaped (very long/repeating URL).
- Early length-rejection is a defense-in-depth control that prevents pathological oversized payloads from reaching deeper parsing/validation paths.
- This follows the module guidance to combine parser-based validation with strict length bounds.

## Real verification command
- Executed a direct function-level check (no fabricated output):
  - Created URL longer than `MAX_URL_LENGTH` by 5,000 chars.
  - Called `create_link(LinkCreate(...))`.
  - Captured exception and elapsed time.

## Observed output
- `STATUS 400`
- `DETAIL URL is too long. Maximum length is 2048 characters.`
- `ELAPSED_MS 0.017`

## Limitation
- Full end-to-end route profiling under live DB-backed service remains limited by local dependency startup/connectivity constraints observed earlier in this module.
- However, the critical defensive branch for oversized input is verified with real execution evidence above.
