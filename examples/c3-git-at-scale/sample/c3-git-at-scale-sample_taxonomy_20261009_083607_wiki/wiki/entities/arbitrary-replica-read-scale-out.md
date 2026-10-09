---
title: Arbitrary replica read scale-out
type: value
id: '3.27'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s01_p14
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
design_points:
- '[[designs/p012|P012]]'
- '[[designs/p022|P022]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Arbitrary replica read scale-out

Adding an arbitrary number of replicas to increase read-only Git throughput.

## Evidence

- **s01_p14** (accepts) · [[sources/s1|Git at any scale]] · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …

## In design points

[[designs/p012|P012]], [[designs/p022|P022]]
