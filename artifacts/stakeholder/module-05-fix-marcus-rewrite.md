# FIX — Marcus email rewritten for VP Eng + Head of Product

**Subject:** Need approval: 8-week front-door upgrade before next peak season

Hi Sarah and David,

**We need your OK to spend 8 weeks (2 engineers) upgrading how traffic enters our product**—the system that almost melted checkout last Black Friday—so we do not repeat a ~47-minute checkout outage in the next peak.

**Why it matters:** Last November we hit our traffic ceiling and checkout slowed hard enough that availability dropped below our promise for about 47 minutes. We are still on aging “front door” software that no longer gets security updates. Waiting raises the odds of another peak-season failure and a longer emergency scramble.

**What we will do (plain language):** Replace the current multi-piece front door with a simpler, modern setup that can shed overload more safely and play nicer with how our apps already run. We will run old and new side-by-side before flipping customers over, aiming for **no planned customer downtime**.

**Honest risks (not buried):**
1. New components must prove they handle **~2× last year’s peak** in a rehearsal—or we **do not cut over**.
2. The new setup uses more server memory (~40+ GB fleet-wide). **We have not yet proven** that leaves enough room for holiday auto-scale. That proof is a **go/no-go** before launch; if it fails, we buy capacity or abort cutover—not “hope.”

**Ask:**
1. Approve the 8-week plan starting [date].  
2. Confirm a **holiday code-freeze window** where we will not cut over.  
3. 20 minutes this week to align on external/status language if anything slips.

Thanks,  
Marcus

*(Optional leave-behind appendix for eng reviewers can keep Kong/Envoy details—out of the stakeholder body.)*
