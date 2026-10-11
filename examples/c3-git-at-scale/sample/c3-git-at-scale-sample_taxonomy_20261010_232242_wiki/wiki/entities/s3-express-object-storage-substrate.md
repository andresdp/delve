---
title: S3 Express object-storage substrate
type: value
id: '10.27'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p10
- s01_p12
- s01_p14
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
design_points:
- '[[designs/p010|P010]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# S3 Express object-storage substrate

A low-latency object-storage tier is selected for high-throughput WAL persistence.

## Evidence

- **s01_p10** (accepts) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
- **s01_p12** (accepts) · [[sources/s1|Git at any scale]] · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
- **s01_p14** (accepts) · [[sources/s1|Git at any scale]] · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …

## In design points

[[designs/p010|P010]]
