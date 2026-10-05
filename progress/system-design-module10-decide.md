# System Design Module 10 DECIDE

Choice: **A** (`decisions.module_10.deploy_strategy = single_container`)

The API already runs create, redirect, in-process click worker, and `/live`/`/ready` in one process. Module 07 kept analytics off the 307 path with a daemon thread, not a second service. One image SHA is one rollback unit — Knight Capital was mixed versions across eight servers; four independently deployed services multiply that.

Gain of a separate worker: scale clicks without scaling HTTP. Cost we cannot pay here: Docker engine down, Redis/Postgres not serving, no Railway token. Rollback of B needs a matched API+worker+migration set.

Tradeoff: a worker retry storm shares the process (pools are already split). B is right when we actually run Redis/Celery.
