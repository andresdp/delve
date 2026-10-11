---
title: Priority scheduling for user updates
type: value
id: '11.2'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s02_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p009|P009]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Priority scheduling for user updates

User-initiated reference updates take priority over maintenance bookkeeping.

## Evidence

- **s02_p06** (accepts) · [[sources/s2|Stretching Spokes]] · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …

## In design points

[[designs/p009|P009]]
