---
type: Design Alternative
title: Single-replica read routing
description: After synchronized publication, each fetch or clone is routed to one repository replica rather than coordinated reads across replicas.
id: '13.8'
dimension: /concepts/repository-placement-and-read-routing.md
accepted_by:
- s01_p07
- s02_p01
- s03_p04
rejected_by: []
passages: 3
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- accepted
- repository-placement-and-read-routing
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Single-replica read routing

After synchronized publication, each fetch or clone is routed to one repository replica rather than coordinated reads across replicas.

## Evidence

- **s01_p07** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s02_p01** (accepts) · [Stretching Spokes](/sources/s2.md) · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
- **s03_p04** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Availability
  > Spokes uses heartbeats, too, but not as the primary failure-detection mechanism. Instead, heartbeats have two purposes: polling system load and providing the all-clear signal after a node has been marked as offline. As soon as a heartbeat succeeds, the node is marked as online again. If the heartbeat succeeds despite ongoing server problems (retrieving system load is almost a no-op), …
