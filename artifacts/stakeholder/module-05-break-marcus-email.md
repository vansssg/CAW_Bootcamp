# Module 05 BREAK — Marcus gateway migration email

## Part 1 — Jargon count (Head of Product would stumble)

Counted distinct unexplained terms/phrases (conservative; many repeats not re-counted):

EOL, Kong, 2.8.x, NGINX, reverse proxy, Lua plugins, rate limiting (as impl detail), JWT validation, mTLS termination, service mesh, zero-trust, east-west, tech debt, autoscaling group, c5.2xlarge, RPS, p95, p99, cascaded, timeout errors, SLO, availability %, Envoy, ingress, Kubernetes, Istio sidecars, circuit breaking, retry budgets, WASM filters, CI/CD, GitOps, observability, StatsD, Grafana, OpenTelemetry, Datadog tenant, blue-green, synthetic load tests, staging, cut over, pod memory overhead, node pool, reserved capacity, autoscaling events.

**Count: ~45+** unexplained tech tokens (starter phrase alone = 3).

## Part 2 — Buried business risk

Second Risk paragraph: **+42.5 GB memory** from sidecars **not validated** against capacity reserved for autoscaling.

**Why it matters to Product:** Under next Black Friday–class spike, cluster may **fail to scale** or **evict/timeout checkout** again—same customer pain as last year’s 47-minute SLO miss—while the email sells “no customer-facing downtime.” Parallel-run claim hides a launch-season capacity risk.

## Part 3 — What Sarah/David needed instead

Open with: Black Friday nearly broke checkout; we want 8 weeks / 2 eng to replace aging front door **before** next peak; **ask:** approve schedule + confirm holiday freeze window; call out **memory/scale validation** as a go/no-go before cutover.
