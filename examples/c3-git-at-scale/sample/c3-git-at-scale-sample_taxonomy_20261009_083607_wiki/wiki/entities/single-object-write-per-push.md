---
title: Single-object write per push
type: value
id: '2.4'
status: rejected
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by: []
rejected_by:
- s01_p10
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- rejected
- write-coordination-and-replica-consistency
---

# Single-object write per push

Issuing one object-storage PUT for every push, which would expose ingestion to object-storage latency.

## Evidence

- **s01_p10** (rejects) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
