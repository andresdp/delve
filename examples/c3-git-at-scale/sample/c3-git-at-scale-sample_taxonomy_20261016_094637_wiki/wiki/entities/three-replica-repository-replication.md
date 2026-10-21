---
type: Design Alternative
title: Three-replica repository replication
description: Each repository maintains a fixed floor of three replicas for consistency, redundancy, and continued push acceptance after one failure.
id: '21.2'
dimension: /concepts/replica-topology.md
accepted_by:
- s01_p07
- s01_p08
- s01_p09
- s01_p12
- s02_p01
- s02_p06
- s03_p01
- s03_p03
- s03_p09
rejected_by: []
passages: 9
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p001.md
- /designs/p010.md
- /designs/p011.md
- /designs/p012.md
- /designs/p024.md
tags:
- value
- accepted
- replica-topology
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Three-replica repository replication

Each repository maintains a fixed floor of three replicas for consistency, redundancy, and continued push acceptance after one failure.

## Evidence

- **s01_p07** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s01_p08** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
- **s01_p09** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s01_p12** (accepts) · [Git at any scale](/sources/s1.md) · Replication
  > Having a write-ahead log in S3 opens a world of possibilities when it comes to scale. We can have \*literally\* any number of replicas, because the scalability of S3 is unmatched and all the replicas catch up directly from there. We perform optimistic replication by sending gossip UDP packets around our cluster. The packets contain all the required metadata for …
- **s02_p01** (accepts) · [Stretching Spokes](/sources/s2.md) · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
- **s02_p06** (accepts) · [Stretching Spokes](/sources/s2.md) · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …
- **s03_p01** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
- **s03_p03** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Availability
  > Spokes’s availability is a function of the availability of underlying servers and networks, and of our ability to detect and route around server and network problems. Individual servers become unavailable pretty frequently. Since rolling out Spokes this past spring, we have had individual servers crash due to a kernel deadlock and faulty RAM chips. Sometimes servers provide degraded service due …
- **s03_p09** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …

## In design points

[P001](/designs/p001.md), [P010](/designs/p010.md), [P011](/designs/p011.md), [P012](/designs/p012.md), [P024](/designs/p024.md)
