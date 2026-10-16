---
title: Replica round-trip coordination latency
type: value
id: '30.19'
status: outcome
dimension: '[[concepts/replica-write-coordination|Replica Write Coordination]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-write-coordination
---

# Replica round-trip coordination latency

Multiple distant-replica round trips consume the write-coordination latency budget.

## Evidence

- **s02_p03** (supports) · [[sources/s2|Stretching Spokes]] · Reducing round-trips
  > Due to the speed of light and other annoying facts, every round-trip communication to a distant replica takes time. For example, a network round-trip across the continental US takes something like 60-80 milliseconds. It wouldn’t take very many round trips to use up our time budget. We use the three-phase commit protocol to update the replicas and additionally use the …
