---
title: Four-round-trip coordination cost
type: value
id: '2.36'
status: outcome
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
merged_from:
- id: '2.43'
  label: Cross-region coordination latency
tags:
- value
- outcome
- write-coordination-and-replica-consistency
---

# Four-round-trip coordination cost

Operational latency incurred by the adopted distant-replica coordination protocol.

## Evidence

- **s02_p03** (supports) · [[sources/s2|Stretching Spokes]] · Reducing round-trips
  > Due to the speed of light and other annoying facts, every round-trip communication to a distant replica takes time. For example, a network round-trip across the continental US takes something like 60-80 milliseconds. It wouldn’t take very many round trips to use up our time budget. We use the three-phase commit protocol to update the replicas and additionally use the …

## Merged from

- {'id': '2.43', 'label': 'Cross-region coordination latency'}
