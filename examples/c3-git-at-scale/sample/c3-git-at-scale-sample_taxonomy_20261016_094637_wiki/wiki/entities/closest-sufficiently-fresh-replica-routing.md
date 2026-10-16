---
title: Closest sufficiently fresh replica routing
type: value
id: '13.7'
status: accepted
dimension: '[[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]]'
accepted_by:
- s02_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p017|P017]]'
tags:
- value
- accepted
- repository-placement-and-read-routing
---

# Closest sufficiently fresh replica routing

Reads route to the geographically closest replica that meets freshness requirements.

## Evidence

- **s02_p06** (accepts) · [[sources/s2|Stretching Spokes]] · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …

## In design points

[[designs/p017|P017]]
