---
title: Replicated compaction output
type: value
id: '2.20'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s01_p13
- s01_p14
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Replicated compaction output

Replicating compacted repository data rather than independently compacting each replica.

## Evidence

- **s01_p13** (accepts) · [[sources/s1|Git at any scale]] · Compaction
  > Write-ahead logs require periodic compaction. You cannot let the log grow unbounded: a full restore replays every entry, so the more entries, the more expensive it becomes. Coincidentally, a normal Git repository \*also\* requires periodic compaction, even though Git is not based on a WAL. We've seen that the fundamental unit of storage in a Git repository is the \*packfile\*. …
- **s01_p14** (accepts) · [[sources/s1|Git at any scale]] · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …
