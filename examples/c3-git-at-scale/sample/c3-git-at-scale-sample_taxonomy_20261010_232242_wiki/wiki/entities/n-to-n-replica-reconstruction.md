---
title: N-to-N replica reconstruction
type: value
id: '10.14'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p12
- s03_p06
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# N-to-N replica reconstruction

Replacement replicas are created across the cluster from any surviving repository copies after failures.

## Evidence

- **s01_p12** (accepts) · [[sources/s1|Git at any scale]] · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
- **s03_p06** (accepts) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
