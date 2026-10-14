---
title: Single-extra-copy topology
type: value
id: '10.3'
status: rejected
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by: []
rejected_by:
- s01_p09
- s03_p05
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- rejected
- replica-topology-and-persistence
---

# Single-extra-copy topology

Keeping only one additional copy is considered sufficient for a single-node failure but rejected because concurrent writes still require consistent serialization.

## Evidence

- **s01_p09** (rejects) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s03_p05** (rejects) · [[sources/s3|Building resilience in Spokes]] · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …
