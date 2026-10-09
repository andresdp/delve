---
title: Batched WAL persistence
type: value
id: '2.5'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s01_p10
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
design_points:
- '[[designs/p007|P007]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Batched WAL persistence

Batching log persistence to amortize object-storage latency and approach local disk throughput.

## Evidence

- **s01_p10** (accepts) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …

## In design points

[[designs/p007|P007]]
