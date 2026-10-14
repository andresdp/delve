---
title: Replica-side repository repacking
type: value
id: '11.38'
status: rejected
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by:
- s01_p13
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- rejected
- repository-service-scaling
---

# Replica-side repository repacking

Each replica independently performs CPU-intensive repository repacking.

## Evidence

- **s01_p13** (rejects) · [[sources/s1|Git at any scale]] · Compaction
  > Write-ahead logs require periodic compaction. You cannot let the log grow unbounded: a full restore replays every entry, so the more entries, the more expensive it becomes. Coincidentally, a normal Git repository \*also\* requires periodic compaction, even though Git is not based on a WAL. We've seen that the fundamental unit of storage in a Git repository is the \*packfile\*. …
