---
title: Single-local-repository synchronization
type: value
id: '30.13'
status: accepted
dimension: '[[concepts/replica-write-coordination|Replica Write Coordination]]'
accepted_by:
- s01_p10
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- replica-write-coordination
---

# Single-local-repository synchronization

Reference transactions synchronize with one local repository rather than a replica quorum.

## Evidence

- **s01_p10** (accepts) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
