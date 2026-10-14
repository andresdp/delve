---
title: Idle-replica overhead
type: value
id: '10.28'
status: outcome
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by: []
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-topology-and-persistence
---

# Idle-replica overhead

Maintaining three mostly idle replicas per small or throwaway repository creates substantial overhead as repository counts proliferate.

## Evidence

- **s01_p08** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
- **s01_p09** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s03_p03** (supports) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes’s availability is a function of the availability of underlying servers and networks, and of our ability to detect and route around server and network problems. Individual servers become unavailable pretty frequently. Since rolling out Spokes this past spring, we have had individual servers crash due to a kernel deadlock and faulty RAM chips. Sometimes servers provide degraded service due …
