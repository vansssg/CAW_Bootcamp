# Module 1 DECIDE — extraction method

Choice: **B categorized matrix** (`decisions.module_01.extraction_method` = categorized by stakeholder × type)

## Why B for SkillSwap

If the PM asks “did we cover providers?”, a PROVIDER section answers in seconds. A flat list of 20+ lines does not flag a missing provider-quality row. The six-week cancel story mixed a functional (“cancel”) with unstated constraints (refund, slot release) in one sentence — a matrix would have shown PLATFORM-Constraint empty for refunds.

Engineers estimate better when “search feels instant” sits under USER-Quality, not next to “browse by category.” Functional vs quality vs constraint changes the work (index vs feature vs business rule).

## Taxonomy I will use

- Functional = verb (book, vet, pay)
- Constraint = fence (15% commission, 3 developers, no double-book)
- Quality = adjective (instant search, testable cancellation)

Blur: 15% commission is a business rule. I will file it under PLATFORM-Constraint and still write a functional “compute payout after commission” so it does not vanish.

## Rejected A

Faster to type; worse at gap-finding. SkillSwap has three stakeholders (learner, provider, platform/admin). Flat list is how “users can cancel” shipped without a policy.

## PM vs engineers

PM: stakeholder sections. Engineers: type rows so quality work is not estimated as a button.
