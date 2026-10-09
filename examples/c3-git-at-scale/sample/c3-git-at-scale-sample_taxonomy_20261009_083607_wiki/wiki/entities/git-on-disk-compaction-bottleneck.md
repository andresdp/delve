---
title: Git on-disk compaction bottleneck
type: value
id: '4.37'
status: outcome
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- outcome
- client-repository-workload-scaling
---

# Git on-disk compaction bottleneck

Git disk compaction becoming the throughput limit at high ingestion scale.

## Evidence

- **s01_p14** (supports) · [[sources/s1|Git at any scale]] · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …
