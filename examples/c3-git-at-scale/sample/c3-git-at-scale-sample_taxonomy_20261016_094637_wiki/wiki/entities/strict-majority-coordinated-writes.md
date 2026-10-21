---
type: Design Alternative
title: Strict-majority coordinated writes
description: Uses three replicas, majority-held exclusive locks, strict-majority acceptance, and replica-wide serialization to prevent conflicting divergent writes.
id: '30.1'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s01_p09
- s01_p12
- s01_p14
- s02_p01
- s03_p05
- s03_p06
- s03_p08
- s03_p09
rejected_by: []
passages: 8
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p022.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Strict-majority coordinated writes

Uses three replicas, majority-held exclusive locks, strict-majority acceptance, and replica-wide serialization to prevent conflicting divergent writes.

## Evidence

- **s01_p09** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s01_p12** (accepts) · [Git at any scale](/sources/s1.md) · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
- **s01_p14** (accepts) · [Git at any scale](/sources/s1.md) · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …
- **s02_p01** (accepts) · [Stretching Spokes](/sources/s2.md) · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
- **s03_p05** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …
- **s03_p06** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
- **s03_p08** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Clean shutdowns
  > We don’t perform “chaos monkey” testing on the Spokes file servers, for the same reasons we prefer to quiesce them before rebooting them: to avoid interrupting long-running reads. That is, we do not reboot them randomly just to confirm that sudden, single-node failures are still (mostly) harmless. Instead of “chaos monkey” testing, we perform rolling reboots as needed, which accomplish …
- **s03_p09** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …

## In design points

[P022](/designs/p022.md)
