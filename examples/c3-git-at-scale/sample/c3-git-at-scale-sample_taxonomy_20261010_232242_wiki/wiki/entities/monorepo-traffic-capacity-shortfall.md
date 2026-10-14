---
title: Monorepo traffic capacity shortfall
type: value
id: '10.29'
status: outcome
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-topology-and-persistence
---

# Monorepo traffic capacity shortfall

Three replicas become insufficient for traffic from massive enterprise monorepos, especially continuous-integration traffic.

## Evidence

- **s01_p08** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
