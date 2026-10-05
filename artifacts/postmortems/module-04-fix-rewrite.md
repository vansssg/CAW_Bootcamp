# Postmortem rewrite (blameless) — OrderProcessor silent drops

*Same facts as the blame-heavy doc; analysis replaced.*

## Summary

On Wednesday afternoon, OrderProcessor v2.14 shipped a config change that removed `warehouse_routing`. For ~2 hours, checkout returned HTTP 200 while orders were not persisted—~1,400 customers charged without an order (~$186k). Detection lagged because monitors only watched HTTP/latency. Automated rollback failed (stale artifact path post-migration); platform completed a manual rollback; payment logs were reprocessed by 16:02.

## Five-Whys (abbrev.)

Charged without orders → 200 without DB write → swallowed missing-config error → deprecated field removed while still required → staging config ≠ prod + success defined as HTTP 200, not durable order.

## Root Cause

The service could return success when order persistence failed, and production health did not include business invariants (orders created). Staging could not reveal the failure mode because its config schema differed from production.

## Contributing Factors

- DEBUG-level logging on swallowed errors  
- No orders-per-minute / payment-vs-order alert  
- Prior email-delay incidents biased first triage hypothesis  
- Rollback automation untested after infra migration  

## Action Items

(Same six system changes as `module-04-orderprocessor-postmortem.md`: fail-closed persist, orders/min alert, reconciliation job, staging config parity, rollback drill, deprecation policy tests — role owners, deadlines, DoD.)

## Lessons Learned

HTTP green ≠ checkout healthy. Deprecation without compat tests is unsafe. Untested rollback is theater. Blameless docs keep near-miss data flowing.
