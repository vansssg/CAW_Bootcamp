# Module 07 — Adaptation note (PM)

**v1 (company bridge):** With Meridian’s company-accounts ask and a 6-day investor demo, we planned a minimal bridge (book-on-behalf name/email; billing on the booker).

**v2 (RBAC — same day):** Meridian IT also requires roles: managers book for employees; employees view-only own bookings; department heads see their department’s bookings. The boolean flag is not enough, so we are adding a **thin role + department** model for the demo — still **not** full org invoicing or a multi-tenant admin product.

In six days you get: browse/book with seeded providers, Meridian users with roles, manager book-on-behalf, employee own-booking view, dept-head department list. You do **not** get: company invoices, polished UI (API/minimal form if time slips), provider self-service, live Stripe (simulate if needed), or advanced search.

**Risk:** authz matrix is the new critical path — if role checks slip, we demo with three scripted accounts and a checklist, not a redesign. **Need from you:** (1) Meridian IT confirm of the three roles + department scope, (2) OK that invoicing waits, (3) names for one manager / one employee / one dept_head in the seed script.
