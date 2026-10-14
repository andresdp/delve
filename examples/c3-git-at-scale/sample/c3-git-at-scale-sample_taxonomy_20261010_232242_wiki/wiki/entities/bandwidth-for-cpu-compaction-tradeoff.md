---
title: Bandwidth-for-CPU compaction tradeoff
type: value
id: '11.61'
status: outcome
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- outcome
- repository-service-scaling
---

# Bandwidth-for-CPU compaction tradeoff

Replica CPU work is reduced by increasing compacted-pack download bandwidth.

## Evidence

- **s01_p13** (supports) · [[sources/s1|Git at any scale]] · Compaction
  > Write-ahead logs require periodic compaction. You cannot let the log grow unbounded: a full restore replays every entry, so the more entries, the more expensive it becomes. Coincidentally, a normal Git repository \*also\* requires periodic compaction, even though Git is not based on a WAL. We've seen that the fundamental unit of storage in a Git repository is the \*packfile\*. …
