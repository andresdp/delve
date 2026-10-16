---
type: Design Alternative
title: Consensus-free write acceptance
description: Any repository instance may accept writes, using storage-level atomic updates instead of elected consensus primaries.
id: '30.4'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s01_p11
- s01_p12
- s03_p09
rejected_by: []
passages: 3
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p012.md
- /designs/p023.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Consensus-free write acceptance

Any repository instance may accept writes, using storage-level atomic updates instead of elected consensus primaries.

## Evidence

- **s01_p11** (accepts) · [Git at any scale](/sources/s1.md) · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
- **s01_p12** (accepts) · [Git at any scale](/sources/s1.md) · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
- **s03_p09** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …

## In design points

[P012](/designs/p012.md), [P023](/designs/p023.md)
