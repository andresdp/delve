---
title: Bookkeeping-update transaction coalescing
type: value
id: '11.1'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s01_p10
- s02_p06
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Bookkeeping-update transaction coalescing

Non-user-critical bookkeeping reference updates are combined to reduce transaction cascades.

## Evidence

- **s01_p10** (accepts) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
- **s02_p06** (accepts) · [[sources/s2|Stretching Spokes]] · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …
