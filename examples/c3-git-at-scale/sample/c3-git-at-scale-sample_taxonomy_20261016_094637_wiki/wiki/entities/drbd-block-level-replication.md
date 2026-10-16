---
type: Design Alternative
title: DRBD block-level replication
description: Repository filesystems are replicated at the block level through DRBD, requiring latency-close replicas.
id: '22.2'
dimension: /concepts/replica-synchronization-mechanism.md
accepted_by: []
rejected_by:
- s01_p05
- s02_p01
- s02_p02
passages: 3
systems:
- /synthesis/systems/gh-fs.md
- /synthesis/systems/gh-spokes.md
tags:
- value
- rejected
- replica-synchronization-mechanism
stance: rejected
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# DRBD block-level replication

Repository filesystems are replicated at the block level through DRBD, requiring latency-close replicas.

## Evidence

- **s01_p05** (rejects) · [Git at any scale](/sources/s1.md) · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
- **s02_p01** (rejects) · [Stretching Spokes](/sources/s2.md) · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
- **s02_p02** (rejects) · [Stretching Spokes](/sources/s2.md) · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
