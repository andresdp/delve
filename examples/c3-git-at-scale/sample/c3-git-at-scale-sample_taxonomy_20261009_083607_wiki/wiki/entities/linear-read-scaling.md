---
title: Linear read scaling
type: value
id: '1.18'
status: outcome
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- outcome
- repository-replica-placement
---

# Linear read scaling

Read throughput increasing linearly as repository replicas are added.

## Evidence

- **s01_p14** (supports) · [[sources/s1|Git at any scale]] · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …
