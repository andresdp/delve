---
title: ETag-validated replica freshness
type: value
id: '10.15'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p12
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
design_points:
- '[[designs/p020|P020]]'
- '[[designs/p022|P022]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# ETag-validated replica freshness

Conditional object-store metadata validation confirms replica freshness before serving reads.

## Evidence

- **s01_p12** (accepts) · [[sources/s1|Git at any scale]] · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …

## In design points

[[designs/p020|P020]], [[designs/p022|P022]]
