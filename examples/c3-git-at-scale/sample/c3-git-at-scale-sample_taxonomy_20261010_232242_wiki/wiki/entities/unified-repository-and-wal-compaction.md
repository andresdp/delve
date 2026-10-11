---
title: Unified repository and WAL compaction
type: value
id: '11.37'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s01_p12
- s01_p13
- s01_p15
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Unified repository and WAL compaction

Compaction updates both the on-disk repository and authoritative log state.

## Evidence

- **s01_p12** (accepts) · [[sources/s1|Git at any scale]] · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
- **s01_p13** (accepts) · [[sources/s1|Git at any scale]] · Compaction
  > Write-ahead logs require periodic compaction. You cannot let the log grow unbounded: a full restore replays every entry, so the more entries, the more expensive it becomes. Coincidentally, a normal Git repository \*also\* requires periodic compaction, even though Git is not based on a WAL. We've seen that the fundamental unit of storage in a Git repository is the \*packfile\*. …
- **s01_p15** (accepts) · [[sources/s1|Git at any scale]] · WAL as truth
  > S3 is a great piece of technology. The whole concept of blob storage that was pioneered with the S3 API has turned out to be a very powerful building block for large data storage systems, and this most definitely also applies to hosting Git repositories. The design presented here is novel on many ways, but it's not the first one …
