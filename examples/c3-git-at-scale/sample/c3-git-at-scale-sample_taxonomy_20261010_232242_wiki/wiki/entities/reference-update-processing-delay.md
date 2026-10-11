---
title: Reference-update processing delay
type: value
id: '11.45'
status: outcome
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- repository-service-scaling
---

# Reference-update processing delay

Large bookkeeping cascades can keep a repository busy and delay or time out user requests.

## Evidence

- **s02_p06** (supports) · [[sources/s2|Stretching Spokes]] · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …
