---
type: Design Alternative
title: Closest sufficiently fresh replica routing
description: Reads route to the geographically closest replica that meets freshness requirements.
id: '13.7'
dimension: /concepts/repository-placement-and-read-routing.md
accepted_by:
- s02_p06
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p017.md
tags:
- value
- accepted
- repository-placement-and-read-routing
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Closest sufficiently fresh replica routing

Reads route to the geographically closest replica that meets freshness requirements.

## Evidence

- **s02_p06** (accepts) · [Stretching Spokes](/sources/s2.md) · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …

## In design points

[P017](/designs/p017.md)
