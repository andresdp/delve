---
title: Proxy-mediated repository replication
type: value
id: '10.9'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p07
- s02_p01
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p017|P017]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# Proxy-mediated repository replication

A proxy transparently forwards each Git push to multiple repository replicas.

## Evidence

- **s01_p07** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s02_p01** (accepts) · [[sources/s2|Stretching Spokes]] · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …

## In design points

[[designs/p017|P017]]
