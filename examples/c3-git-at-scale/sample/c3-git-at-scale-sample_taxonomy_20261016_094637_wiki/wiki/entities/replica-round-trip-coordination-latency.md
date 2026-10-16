---
type: Outcome
title: Replica round-trip coordination latency
description: Multiple distant-replica round trips consume the write-coordination latency budget.
id: '30.19'
dimension: /concepts/replica-write-coordination.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- outcome
- replica-write-coordination
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica round-trip coordination latency

Multiple distant-replica round trips consume the write-coordination latency budget.

## Evidence

- **s02_p03** (supports) · [Stretching Spokes](/sources/s2.md) · Reducing round-trips
  > Due to the speed of light and other annoying facts, every round-trip communication to a distant replica takes time. For example, a network round-trip across the continental US takes something like 60-80 milliseconds. It wouldn’t take very many round trips to use up our time budget. We use the three-phase commit protocol to update the replicas and additionally use the …
