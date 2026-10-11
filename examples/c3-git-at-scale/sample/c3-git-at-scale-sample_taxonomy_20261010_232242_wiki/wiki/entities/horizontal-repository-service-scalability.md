---
title: Horizontal repository-service scalability
type: value
id: '11.50'
status: outcome
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- outcome
- repository-service-scaling
---

# Horizontal repository-service scalability

Improves the ability to scale repository-serving capacity across machines and disks.

## Evidence

- **s01_p05** (supports) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
- **s01_p14** (supports) · [[sources/s1|Git at any scale]] · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …
