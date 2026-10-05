# Module 2 BREAK — cycle

PM added: vetting happens **through the admin dashboard**. Combined with “dashboard needs provider data” and “provider data is only real after vetting”:

```
W3 Vetting --H--> W12 Admin dashboard --H--> W2 Provider data --H--> W3 Vetting
```

Reordering W3, W12, W2 never starts: each waits. Not a scheduling bug. A **definition** bug.

## Weakest assumption

**“Provider data does not exist until vetted.”** That collapses submit vs go-live. A pending profile can sit in W2 with `status=pending` before any dashboard exists.

Second-weak: **“Vetting needs the full admin dashboard.”** A CSV + `approve_provider(id)` script can cut the first providers without W12.

Dashboard → “some provider records” is the least questionable (UI needs rows). The cycle is created by treating those rows as only-post-vetting and treating W12 as the only approval UI.

## PM language (no DAG)

“Approval, the profile form, and the admin screen each wait for one of the others, so we cannot start any of them as currently written. We have to split ‘provider submitted a profile’ from ‘provider is live,’ or give ops a tiny approve tool that is not the full dashboard.”
