---
title: Degraded-correctness healthy-speed behavior
type: value
id: '6.40'
status: outcome
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- outcome
- write-commitment-and-consistency
---

# Degraded-correctness healthy-speed behavior

The replication design preserves correctness during degradation while retaining fast healthy reads.

## Evidence

- **s01_p12** (supports) · [[sources/s1|Git at any scale]] · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
