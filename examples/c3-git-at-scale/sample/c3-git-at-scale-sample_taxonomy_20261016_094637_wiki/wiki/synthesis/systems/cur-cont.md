---
title: Cursor Continuity and Origin
type: system
code: CUR-CONT
organization: Cursor
dimensions: 6
tags:
- system
---

# Cursor Continuity and Origin

Write-ahead log in S3 as the source of truth, repositories on disk as a warm cache.

Values adopted by passages whose primary system is `CUR-CONT` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]] ⚠ | • [[entities/core-git-capability-consolidation|Core Git capability consolidation]] (1)<br>• [[entities/native-git-scalability-improvements|Native Git scalability improvements]] (1)<br>• [[entities/repository-performance-tracing|Repository performance tracing]] (1) |  |
| [[concepts/compaction-maintenance-technique|Compaction Maintenance Technique]] | • [[entities/background-incremental-maintenance|Background incremental maintenance]] (1) |  |
| [[concepts/replica-synchronization-mechanism|Replica Synchronization Mechanism]] | • [[entities/git-level-distribution|Git-level distribution]] (1) |  |
| [[concepts/replica-topology|Replica Topology]] | • [[entities/three-replica-repository-replication|Three-replica repository replication]] (1) |  |
| [[concepts/replica-write-coordination|Replica Write Coordination]] ⚠ | • [[entities/consensus-free-write-acceptance|Consensus-free write acceptance]] (2)<br>• [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] (2)<br>• [[entities/single-local-repository-synchronization|Single-local-repository synchronization]] (1) |  |
| [[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]] ⚠ | • [[entities/rendezvous-hashed-repository-routing|Rendezvous-hashed repository routing]] (1)<br>• [[entities/stale-routing-recovery|Stale-routing recovery]] (1)<br>• [[entities/stateless-repository-placement|Stateless repository placement]] (1) | • [[entities/per-server-repository-location-tracking|Per-server repository location tracking]] (1) |

## Attested design points

[[designs/p001|P001]], [[designs/p012|P012]], [[designs/p022|P022]], [[designs/p023|P023]]
