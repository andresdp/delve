---
title: Co-located filesystem replica placement
type: value
id: '10.26'
status: rejected
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by: []
rejected_by:
- s02_p02
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p013|P013]]'
tags:
- value
- rejected
- replica-topology-and-persistence
---

# Co-located filesystem replica placement

Keeps filesystem replicas adjacent to control replication latency, rather than separating them across racks or sites.

## Evidence

- **s02_p02** (rejects) · [[sources/s2|Stretching Spokes]] · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …

## In design points

[[designs/p013|P013]]
