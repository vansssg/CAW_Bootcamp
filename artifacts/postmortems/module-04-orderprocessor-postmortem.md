# Postmortem: OrderProcessor silent order drops (v2.14)

**Service:** OrderProcessor (checkout)  
**Format:** Five-whys (DECIDE B)  
**Severity:** High — ~1,400 charged-but-not-created orders (~$186k), ~2h customer impact  
**Status:** Resolved 16:02 (orders reprocessed)

---

## 1. Summary

On a Wednesday afternoon, OrderProcessor v2.14 removed the deprecated `warehouse_routing` config field. For ~2 hours (14:00–15:34), checkout returned HTTP 200 success while orders were not persisted—customers were charged with no confirmation email and no order record. About 1,400 orders (~$186,000) were affected. Monitoring stayed green (200s/latency only). Rollback automation failed; platform completed a manual rollback to v2.13 at 15:34, and payment-log reprocessing finished by 16:02.

---

## 2. Five-Whys Analysis

**Symptom:** Customers were charged but orders were not created.

1. **Why?** OrderProcessor returned 200 without writing an order row.  
2. **Why?** Creating an order threw on missing `warehouse_routing`; a broad try/except caught it, logged at DEBUG, and still returned success.  
3. **Why?** v2.14 removed `warehouse_routing` from config while v2.13 still required it at runtime (deprecation != safe removal).  
4. **Why?** Staging uses a different config schema than production and never had `warehouse_routing`, so the bad path was invisible in pre-prod.  
5. **Why (systemic)?** There is no **business-level invariant check** (orders created vs payments authorized) and no **config compatibility / canary** gate that fails deploys when production-required keys disappear—plus success is defined as HTTP 200, not “order durable.”

*(Parallel contributing chain for duration: no “orders/min = 0” alert; CS signal dismissed as email delay; untested rollback script.)*

---

## 3. Root Cause(s)

The system allowed a config removal to become a **silent success path**: errors during persistence were swallowed, clients were told OK, and health checks only watched HTTP/latency—not order creation. Staging/prod config skew meant the failure mode could not appear before production. Deprecation policy covered code cleanliness, not **runtime compatibility** or **semantic success**.

---

## 4. Contributing Factors

| Factor | How it amplified damage |
|--------|-------------------------|
| DEBUG-only log on swallowed exception | Invisible in normal log severity filters |
| No orders-per-minute / payment-vs-order lag alert | ~55+ minutes until DB check |
| On-call assumed email delay from prior pattern | Investigation delayed 14:23–14:38 |
| Untested rollback after infra migration | Extra ~26 minutes until manual restore |
| Staging config schema ≠ production | Pre-prod green, prod broken |

---

## 5. Action Items

| # | Description | Owner (role) | Deadline | Definition of done |
|---|-------------|--------------|----------|-------------------|
| 1 | Fail closed on order persist errors: never return 200 if order not committed; map to 5xx/409 with client-safe body | OrderProcessor tech lead | 7 days | Integration test: missing required config → non-2xx and zero payment-without-order in test harness |
| 2 | Add metric `orders_created_per_min`; alert `#ops-alerts` + page on-call if value drops below 10 for more than 5 consecutive minutes while checkout QPS > 10 | Observability / on-call rotation owner | 7 days | Alert fires in staging chaos test; runbook link in alert |
| 3 | Payment-authorized vs order-created reconciliation job every 1 min; auto-ticket mismatches | Payments + OrderProcessor leads | 14 days | Job detects injected mismatch in staging within 2 min |
| 4 | Staging must load **production-shaped** config (or contract test of required keys) before deploy | Platform + OrderProcessor leads | 14 days | CI fails if required prod keys absent from staging fixture |
| 5 | Fix and quarterly-test rollback automation (current artifact paths) | Platform team lead | 14 days | Documented rollback drill passes in staging; calendar invite recurring |
| 6 | Deprecation policy: remove field only after two versions with explicit “absent key” behavior tests | Eng manager, checkout | 30 days | Policy wiki updated; checklist item on release template |

**Blameless note:** The engineer followed the written deprecation policy. The failure is systemic (success semantics, monitoring, staging fidelity, rollback readiness)—not individual negligence.

---

## 6. Lessons Learned

- HTTP 200 is not a business success signal for checkout.
- Deprecation without runtime/compat tests is a landmine, not hygiene.
- Untested rollback is not a rollback plan.
- Prior “email delay” incidents trained a wrong first hypothesis—pair CS signals with order-write metrics.

---

## Appendix — Compact timeline (reference only)

14:00 deploy v2.14 → 14:22 social/CS symptoms → 14:38 investigate → 14:55 DB empty since 14:00 → 15:08 rollback script fail → 15:34 manual rollback → 16:02 reprocess complete.
