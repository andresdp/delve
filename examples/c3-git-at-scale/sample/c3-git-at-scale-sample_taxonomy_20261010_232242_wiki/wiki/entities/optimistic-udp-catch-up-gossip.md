---
title: Optimistic UDP catch-up gossip
type: value
id: '10.19'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p12
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# Optimistic UDP catch-up gossip

Replicas exchange catch-up metadata through lossy gossip while durable reads independently validate freshness.

## Evidence

- **s01_p12** (accepts) · [[sources/s1|Git at any scale]] · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
