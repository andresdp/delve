---
title: Periodic repository compaction
type: value
id: '11.40'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s01_p13
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Periodic repository compaction

Repository compaction runs periodically to bound packfile growth and lookup cost.

## Evidence

- **s01_p13** (accepts) · [[sources/s1|Git at any scale]] · Compaction
  > Write-ahead logs require periodic compaction. You cannot let the log grow unbounded: a full restore replays every entry, so the more entries, the more expensive it becomes. Coincidentally, a normal Git repository \*also\* requires periodic compaction, even though Git is not based on a WAL. We've seen that the fundamental unit of storage in a Git repository is the \*packfile\*. …
