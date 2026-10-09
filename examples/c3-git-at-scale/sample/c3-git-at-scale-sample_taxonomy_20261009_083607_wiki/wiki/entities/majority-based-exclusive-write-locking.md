---
title: Majority-based exclusive write locking
type: value
id: '2.14'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s02_p03
- s03_p05
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Majority-based exclusive write locking

Acquiring exclusive locks across a replica majority before writes.

## Evidence

- **s02_p03** (accepts) · [[sources/s2|Stretching Spokes]] · Reducing round-trips
  > Due to the speed of light and other annoying facts, every round-trip communication to a distant replica takes time. For example, a network round-trip across the continental US takes something like 60-80 milliseconds. It wouldn’t take very many round trips to use up our time budget. We use the three-phase commit protocol to update the replicas and additionally use the …
- **s03_p05** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …
