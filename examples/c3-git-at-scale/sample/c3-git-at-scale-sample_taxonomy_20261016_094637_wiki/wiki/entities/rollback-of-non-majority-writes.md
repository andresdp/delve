---
type: Design Alternative
title: Rollback of non-majority writes
description: Writes failing majority agreement are reverted where applied to preserve surviving replica agreement.
id: '30.6'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s03_p06
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p019.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Rollback of non-majority writes

Writes failing majority agreement are reverted where applied to preserve surviving replica agreement.

## Evidence

- **s03_p06** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …

## In design points

[P019](/designs/p019.md)
