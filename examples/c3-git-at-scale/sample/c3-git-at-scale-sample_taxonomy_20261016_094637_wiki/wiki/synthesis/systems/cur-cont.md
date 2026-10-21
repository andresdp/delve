---
type: System
title: Cursor Continuity and Origin
description: Write-ahead log in S3 as the source of truth, repositories on disk as a warm cache.
code: CUR-CONT
organization: Cursor
dimensions: 6
tags:
- system
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Cursor Continuity and Origin

Write-ahead log in S3 as the source of truth, repositories on disk as a warm cache.

Values adopted by passages whose primary system is `CUR-CONT` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [Client Repository Performance Strategy](/concepts/client-repository-performance-strategy.md) ⚠ | • [Core Git capability consolidation](/entities/core-git-capability-consolidation.md) (1)<br>• [Native Git scalability improvements](/entities/native-git-scalability-improvements.md) (1)<br>• [Repository performance tracing](/entities/repository-performance-tracing.md) (1) |  |
| [Compaction Maintenance Technique](/concepts/compaction-maintenance-technique.md) | • [Background incremental maintenance](/entities/background-incremental-maintenance.md) (1) |  |
| [Replica Synchronization Mechanism](/concepts/replica-synchronization-mechanism.md) | • [Git-level distribution](/entities/git-level-distribution.md) (1) |  |
| [Replica Topology](/concepts/replica-topology.md) | • [Three-replica repository replication](/entities/three-replica-repository-replication.md) (1) |  |
| [Replica Write Coordination](/concepts/replica-write-coordination.md) ⚠ | • [Consensus-free write acceptance](/entities/consensus-free-write-acceptance.md) (2)<br>• [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) (2)<br>• [Single-local-repository synchronization](/entities/single-local-repository-synchronization.md) (1) |  |
| [Repository Placement and Read Routing](/concepts/repository-placement-and-read-routing.md) ⚠ | • [Rendezvous-hashed repository routing](/entities/rendezvous-hashed-repository-routing.md) (1)<br>• [Stale-routing recovery](/entities/stale-routing-recovery.md) (1)<br>• [Stateless repository placement](/entities/stateless-repository-placement.md) (1) | • [Per-server repository location tracking](/entities/per-server-repository-location-tracking.md) (1) |

## Attested design points

[P001](/designs/p001.md), [P012](/designs/p012.md), [P022](/designs/p022.md), [P023](/designs/p023.md)
