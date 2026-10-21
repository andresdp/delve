---
type: Design Alternative
title: Per-write voting without a primary
description: Each write directly determines its winning order and outcome rather than following a primary's global ordering.
id: '30.5'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s03_p06
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p013.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Per-write voting without a primary

Each write directly determines its winning order and outcome rather than following a primary's global ordering.

## Evidence

- **s03_p06** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …

## In design points

[P013](/designs/p013.md)
