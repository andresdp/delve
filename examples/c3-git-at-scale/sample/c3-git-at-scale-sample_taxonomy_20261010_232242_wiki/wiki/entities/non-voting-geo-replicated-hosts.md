---
title: Non-voting geo-replicated hosts
type: value
id: '6.5'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s02_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Non-voting geo-replicated hosts

Geographically replicated hosts do not vote, allowing primary pushes to continue when a replicated host is unreachable.

## Evidence

- **s02_p06** (accepts) · [[sources/s2|Stretching Spokes]] · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …
