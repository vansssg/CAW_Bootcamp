# RFC: Public API Rate Limiting (Lightweight)

**Status:** Request for Comments  
**Author:** SkillSwap / platform API  
**Audience:** Senior engineers (API, infra, support)  
**Format:** Lightweight (problem / proposal / alternatives / risks / open questions)

---

## 1. Problem Statement

Our public API has no automated throttle. Last month one customer sent ~50k req/min and degraded latency for everyone else. On-call mitigated by manually editing a config file and redeploying at 2 AM — slow, error-prone, and not a product. Product also wants a paid tier with **guaranteed** limits; we have nothing to hang that SKU on. Uncontrolled traffic + manual key blocks = shared-tenant risk and blocked revenue.

## 2. Proposed Approach

Add **gateway-enforced rate limiting** with a **Redis-backed token bucket** keyed by API key (fallback: IP for unauthenticated probes).

- **Where:** API gateway / edge middleware in front of app servers (one choke point; apps stay dumb).
- **Algorithm:** Token bucket — burst allowance + steady refill; better UX than fixed-window cliffs.
- **Storage:** Shared Redis so multi-instance counts stay consistent (in-memory per node lets abusers fan out).
- **Response:** HTTP `429` with `{ "error": { "code": "rate_limited", "message": "..." } }`, plus `Retry-After` and `X-RateLimit-Remaining` headers.
- **Ops:** Default free-tier limits in config; paid-tier limits as keyed overrides (no redeploy to ban — flip limit to 0 or revoke key via admin API).
- **Observability:** Metric `api_rate_limit_exceeded_total{key_hash,tier}`; alert on sustained 429 storms.

Rough ASCII:

```
Client → Gateway (token bucket / Redis) → API
              │
              └─ 429 + Retry-After if empty
```

## 3. Alternatives Considered

| Alternative | Pros | Cons | Why not now |
|-------------|------|------|-------------|
| **A. App-level middleware only** | Fast to ship in one service | Every new service reimplements; inconsistent; bypass via other entrypoints | Gateway is the real front door |
| **B. Fixed-window counter in Redis** | Simpler mental model | Burst at window edges (stampede); worse for “guaranteed” paid tiers | Token bucket matches product language |
| **C. WAF / cloud vendor rate limit only** | Managed | Coarse; hard to map per-API-key product tiers; vendor lock | Keep control of key→tier mapping |

(Doing nothing is covered under Risks.)

## 4. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Redis outage fails open → abuse returns | Fail **closed** for public API with cached last-known limit; page on Redis down |
| False positives on shared corporate NATs | Prefer API-key buckets; IP only for anonymous; support allowlist |
| Latency added on hot path | Redis same-AZ; pipeline GET/SET; SLO: abort rollout if gateway p99 rises >5ms for 10m vs baseline; rollback prior gateway config |
| Paid-tier SKU before limits exist | Ship limiting MVP before marketing launch |
| **Do nothing** | Repeat multi-tenant brownouts; forever 2 AM config edits; cannot sell guaranteed tiers |

## 5. Open Questions

1. Infra: do edge load balancers / gateways already support custom Lua/Redis plugins, or do we add a sidecar?
2. Product: exact free vs paid bucket sizes and burst multipliers?
3. Support: self-serve “why was I limited?” page vs ticket-only?
4. Security: should we rate-limit by OAuth client_id separately from API key?
5. Compliance: any customer contracts promising unlimited API today?

---

**Ask:** Please comment on fail-open vs fail-closed and whether gateway ownership sits with infra or API platform.
