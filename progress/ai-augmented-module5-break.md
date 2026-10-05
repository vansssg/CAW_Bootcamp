# AI-Augmented Engineering Module 05 BREAK

Round 3 "reconnection/heartbeat" closed the socket after the first dispatch (`DROP_AFTER_FIRST_EVENT = True`). Connection opens, first `invitation.created` delivers, then silent close — no error log. Second event never arrives.

This is surface-looking (one close) but caused by context pollution: latest instruction (reconnect/heartbeat) overwrote a Round 1 win (stable writer loop). Structural bus is still 4; delivery regressed.

Measured (`python -m app.scripts.module05_activity_break`):
BREAK_FIRST_EVENT_OK True; BREAK_SECOND_EVENT_MISSING True; BREAK_SILENT_CLOSE True.
