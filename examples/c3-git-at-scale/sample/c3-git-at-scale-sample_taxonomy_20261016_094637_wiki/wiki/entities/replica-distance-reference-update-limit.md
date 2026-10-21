---
type: Outcome
title: Replica-distance reference-update limit
description: Geographic replica latency bounds sustainable per-repository reference-update throughput.
id: '30.15'
dimension: /concepts/replica-write-coordination.md
accepted_by: []
rejected_by: []
passages: 4
systems:
- /synthesis/systems/gh-spokes.md
merged_from:
- id: '30.9'
  label: Per-repository reference-update latency budget
tags:
- value
- outcome
- replica-write-coordination
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica-distance reference-update limit

Geographic replica latency bounds sustainable per-repository reference-update throughput.

## Evidence

- **s01_p07** (supports) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s02_p01** (supports) · [Stretching Spokes](/sources/s2.md) · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
- **s02_p02** (supports) · [Stretching Spokes](/sources/s2.md) · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
- **s02_p03** (supports) · [Stretching Spokes](/sources/s2.md) · Reducing round-trips
  > Due to the speed of light and other annoying facts, every round-trip communication to a distant replica takes time. For example, a network round-trip across the continental US takes something like 60-80 milliseconds. It wouldn’t take very many round trips to use up our time budget. We use the three-phase commit protocol to update the replicas and additionally use the …

## Merged from

- {'id': '30.9', 'label': 'Per-repository reference-update latency budget'}
