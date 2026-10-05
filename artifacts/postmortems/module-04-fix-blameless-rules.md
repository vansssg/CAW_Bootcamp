# Module 04 FIX — rewrite rules vs blame-heavy doc

Replace named blame with system facts:

| Blame-heavy | Blameless rewrite |
|-------------|-------------------|
| John removed field | Deploy v2.14 removed `warehouse_routing` while runtime still required it |
| Maria should have… | First CS signal interpreted as email delay (prior pattern); no order-write alert to contradict |
| John will be more careful | Action: fail-closed persist + config compat CI |
| Remind team… | Action: deprecation policy requires absent-key tests |
| Maria should set up monitoring | Action: `orders_created_per_min` alert with threshold (role-owned) |

Our `module-04-orderprocessor-postmortem.md` already follows these rules—no further rewrite needed beyond VERIFY tweaks already applied.
