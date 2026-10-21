---
type: Design Alternative
title: Single-extra-copy replication
description: Keeps only one additional copy, sufficient for a single-node failure but insufficient for majority-based coordination of concurrent writes.
id: '21.1'
dimension: /concepts/replica-topology.md
accepted_by: []
rejected_by:
- s01_p08
- s03_p05
passages: 2
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p015.md
- /designs/p021.md
tags:
- value
- rejected
- replica-topology
stance: rejected
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Single-extra-copy replication

Keeps only one additional copy, sufficient for a single-node failure but insufficient for majority-based coordination of concurrent writes.

## Evidence

- **s01_p08** (rejects) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
- **s03_p05** (rejects) · [Building resilience in Spokes](/sources/s3.md) · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …

## In design points

[P015](/designs/p015.md), [P021](/designs/p021.md)
