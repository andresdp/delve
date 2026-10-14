---
title: Low-latency replica placement
type: value
id: '10.10'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s02_p01
- s02_p02
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# Low-latency replica placement

Replicas are placed near enough to coordinate updates within acceptable inter-replica communication latency.

## Evidence

- **s02_p01** (accepts) · [[sources/s2|Stretching Spokes]] · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
- **s02_p02** (accepts) · [[sources/s2|Stretching Spokes]] · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
