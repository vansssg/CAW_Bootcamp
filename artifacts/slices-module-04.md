# SkillSwap Vertical Slices

## Slice 1: Browse and Book (Seeded Provider)

### Scope
- User can view seeded providers.
- User can select one provider and one service.
- User can choose from hardcoded available slots.
- User can submit a booking request.
- System creates a booking record.
- User sees booking confirmation.

### Anti-scope
- No authentication or user accounts.
- No real provider onboarding.
- No provider dashboard.
- No search or filtering.
- No payments.
- No email/SMS notifications.
- No cancellation or refunds.
- No reviews or ratings.
- No dynamic availability management.
- No double-booking prevention.

### Dependencies
- None.

### Acceptance criteria
- A non-technical user can open the marketplace.
- User can choose a seeded provider and service.
- User can select a slot and click book.
- Confirmation shows booking ID, provider name, service, and booked time.
- Refreshing the page verifies the booking persists (stored, not in-memory).

### Complexity
- S


## Slice 1.5: Payment Spike (Stripe Test Mode)

**Hypothesis:** Can money flow through the platform via Stripe test mode without integrating payments into the booking flow?

**Placement:** Parallel to Slice 1 (can start after Slice 1 demo path is stable; does not block Slice 2).

### Scope
- Standalone `/payment-demo` page with a fixed test amount.
- Create Stripe test-mode PaymentIntent and complete checkout.
- Show success/failure result on-screen (payment reference + amount).
- Document env vars required (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`).

### Anti-scope
- Not integrated into Slice 1 booking flow.
- No webhooks beyond minimal client-side success confirmation.
- No refunds, payouts, or commission logic.
- No booking state changes tied to payment.
- No production keys or live charges.

### Dependencies
- None (runs in parallel with Slice 1; optional soft dependency on app shell from Slice 1 UI).

### Acceptance criteria
- Open `/payment-demo`, enter test card `4242…`, submit payment.
- Page shows success with a payment reference ID and charged amount.
- Failed test card shows a clear error without breaking the app.

### Complexity
- S (2–4 hours)

### PM message
> We will demo two thin proofs next Friday: Slice 1 shows end-to-end booking; Slice 1.5 shows Stripe test-mode money flow on a standalone page. This satisfies the investor payment ask without mixing payment integration risk into the booking validation slice. Full booking+payment integration remains in Slice 5 per the risk plan.


## Slice 2: User & Provider Identity Ownership

### Scope
- Add minimal identity model with user and provider roles.
- Associate bookings with users.
- Allow users to view their own bookings.
- Create provider identity required for future listing ownership.
- Restrict users from accessing other users' bookings.

### Anti-scope
- No social login.
- No advanced user profiles.
- No complex permission system.
- No provider analytics.
- No enterprise role management.

### Dependencies
- Slice 1: Browse and Book (Seeded Provider).

### Acceptance criteria
- A user can create a booking linked to their identity.
- A provider identity exists and can be used for future provider actions.
- Users cannot access another user's bookings.

### Complexity
- M


## Slice 3: Provider Self-Service Listing and Availability

### Scope
- Providers can create and update service listings.
- Providers can define available slots.
- Marketplace displays provider-managed data.

### Anti-scope
- No provider analytics.
- No advanced scheduling rules.
- No calendar integrations.
- No automated reminders.
- No provider payouts.

### Dependencies
- Slice 1: Browse and Book (Seeded Provider).
- Slice 2: User & Provider Identity Ownership.

### Acceptance criteria
- A provider can create a service.
- A provider can add available slots.
- A user can see provider-created services and slots.

### Complexity
- M


## Slice 4: Real Availability and Booking Reliability

### Scope
- Validate slot availability before booking.
- Prevent multiple users from booking the same slot.
- Handle conflicting booking attempts safely.

### Anti-scope
- No advanced optimization.
- No waitlists.
- No recurring schedules.
- No timezone handling.
- No complex availability rules.
- No payment required to book.

### Dependencies
- Slice 1: Browse and Book (Seeded Provider).
- Slice 2: User & Provider Identity Ownership.
- Slice 3: Provider Self-Service Listing and Availability.

### Acceptance criteria
- Two users attempt to book the same slot.
- Only one booking succeeds.
- The other user receives a clear unavailable response.

### Complexity
- L


## Slice 5: Payments and Cancellation Flow

**Note:** Slice 1.5 proves payment feasibility only. This slice integrates payment into the booking lifecycle.

### Scope
- Add payment intent handling.
- Track payment state.
- Allow booking cancellation with defined rules.
- Handle refund states.

### Anti-scope
- No real payment provider integration initially.
- No complex refund policies.
- No subscriptions.
- No marketplace payouts.

### Dependencies
- Slice 4: Real Availability and Booking Reliability.

### Acceptance criteria
- User can complete a payment simulation.
- Booking reflects payment state.
- Cancellation updates booking status correctly.

### Complexity
- L
