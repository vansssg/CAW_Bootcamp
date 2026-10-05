# System Design Module 06 REFLECT

Cache-aside. Redis is optional; SoT is the owner-scoped store. TTL 60s. Invalidate on PATCH/DELETE.

Caching is not free: skipping invalidate served the old Location after PATCH.

Abuse twist implemented: redirect 429 after 8 hits.
