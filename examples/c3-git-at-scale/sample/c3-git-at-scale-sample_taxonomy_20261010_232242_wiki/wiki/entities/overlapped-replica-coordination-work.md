---
title: Overlapped replica coordination work
type: value
id: '6.12'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s02_p03
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Overlapped replica coordination work

Useful locking, checksum, and database work proceeds while replica network waits are outstanding.

## Evidence

- **s02_p03** (accepts) · [[sources/s2|Stretching Spokes]] · Reducing round-trips
  > Due to the speed of light and other annoying facts, every round-trip communication to a distant replica takes time. For example, a network round-trip across the continental US takes something like 60-80 milliseconds. It wouldn’t take very many round trips to use up our time budget. We use the three-phase commit protocol to update the replicas and additionally use the …
