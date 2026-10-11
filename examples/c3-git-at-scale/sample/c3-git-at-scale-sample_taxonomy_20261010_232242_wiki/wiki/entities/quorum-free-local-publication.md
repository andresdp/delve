---
title: Quorum-free local publication
type: value
id: '6.30'
status: rejected
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by: []
rejected_by:
- s01_p10
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- rejected
- write-commitment-and-consistency
---

# Quorum-free local publication

Synchronizing reference publication with one local repository instead of a quorum of replicas.

## Evidence

- **s01_p10** (rejects) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
