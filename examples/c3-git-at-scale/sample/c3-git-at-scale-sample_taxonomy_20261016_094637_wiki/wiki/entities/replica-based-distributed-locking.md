---
type: Design Alternative
title: Replica-based distributed locking
description: Replicas provide distributed locks that order coordinated database updates.
id: '30.8'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s02_p03
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica-based distributed locking

Replicas provide distributed locks that order coordinated database updates.

## Evidence

- **s02_p03** (accepts) · [Stretching Spokes](/sources/s2.md) · Reducing round-trips
  > Due to the speed of light and other annoying facts, every round-trip communication to a distant replica takes time. For example, a network round-trip across the continental US takes something like 60-80 milliseconds. It wouldn’t take very many round trips to use up our time budget. We use the three-phase commit protocol to update the replicas and additionally use the …
