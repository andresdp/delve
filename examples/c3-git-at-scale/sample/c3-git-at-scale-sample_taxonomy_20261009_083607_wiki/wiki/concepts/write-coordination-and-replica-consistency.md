---
title: Write Coordination and Replica Consistency
type: dimension
id: '2'
core: true
values: 41
candidate_values: 34
outcomes: 7
evidence:
  codes: 63
  documents: 18
  sources: 4
relations:
- constrains [[concepts/repository-replica-placement|Repository Replica Placement]]
- consequence [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]
- consequence [[concepts/repository-replica-placement|Repository Replica Placement]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Write Coordination and Replica Consistency

How are repository state changes coordinated, persisted, ordered, and made consistent across replicas?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/batched-wal-persistence|Batched WAL persistence]] | accepted | 1 |
| [[entities/concurrent-write-elimination|Concurrent-write elimination]] | accepted | 1 |
| [[entities/consistency-first-write-admission|Consistency-first write admission]] | accepted | 1 |
| [[entities/cross-region-replica-coordination|Cross-region replica coordination]] | accepted | 3 |
| [[entities/durability-before-acknowledgment|Durability-before-acknowledgment]] | accepted | 2 |
| [[entities/fully-consistent-replica-synchronization|Fully consistent replica synchronization]] | accepted | 2 |
| [[entities/incremental-geometric-repository-compaction|Incremental geometric repository compaction]] | accepted | 3 |
| [[entities/local-nvme-git-repository|Local NVMe Git repository]] | accepted | 3 |
| [[entities/majority-based-exclusive-write-locking|Majority-based exclusive write locking]] | accepted | 2 |
| [[entities/majority-based-write-acceptance|Majority-based write acceptance]] | accepted | 5 |
| [[entities/minimum-two-replica-write-commitment|Minimum two-replica write commitment]] | accepted | 1 |
| [[entities/orchestrated-push-fan-out|Orchestrated push fan-out]] | accepted | 1 |
| [[entities/packfile-level-replication|Packfile-level replication]] | accepted | 1 |
| [[entities/per-update-latency-budget|Per-update latency budget]] | accepted | 2 |
| [[entities/per-write-voting-protocol|Per-write voting protocol]] | accepted | 1 |
| [[entities/periodic-repository-compaction|Periodic repository compaction]] | accepted | 1 |
| [[entities/prepared-reference-locking|Prepared reference locking]] | accepted | 3 |
| [[entities/primary-only-repository-compaction|Primary-only repository compaction]] | accepted | 1 |
| [[entities/read-preserving-write-path-optimization|Read-preserving write-path optimization]] | accepted | 2 |
| [[entities/reference-transaction-publication-gate|Reference-transaction publication gate]] | accepted | 2 |
| [[entities/replica-rollback-for-failed-quorum|Replica rollback for failed quorum]] | accepted | 2 |
| [[entities/replica-wide-write-order-serialization|Replica-wide write-order serialization]] | accepted | 2 |
| [[entities/replicated-compaction-output|Replicated compaction output]] | accepted | 2 |
| [[entities/s3-express-one-zone-wal-storage|S3 Express One Zone WAL storage]] | accepted | 2 |
| [[entities/s3-compatible-write-ahead-log|S3-compatible write-ahead log]] | accepted | 2 |
| [[entities/three-phase-reference-commit|Three-phase reference commit]] | accepted | 4 |
| [[entities/wal-first-storage-architecture|WAL-first storage architecture]] | accepted | 2 |
| [[entities/wal-propagated-compaction-events|WAL-propagated compaction events]] | accepted | 1 |
| [[entities/git-level-distribution|Git-level distribution]] | mixed | 2 |
| [[entities/distributed-object-level-git-storage|Distributed object-level Git storage]] | rejected | 1 |
| [[entities/eventually-consistent-repository-views|Eventually consistent repository views]] | rejected | 1 |
| [[entities/replica-local-repository-repacking|Replica-local repository repacking]] | rejected | 1 |
| [[entities/single-object-write-per-push|Single-object write per push]] | rejected | 1 |
| [[entities/single-primary-write-ordering|Single-primary write ordering]] | rejected | 1 |
| [[entities/concurrent-replica-maintenance-availability-risk|Concurrent replica maintenance availability risk]] | outcome | 1 |
| [[entities/four-round-trip-coordination-cost|Four-round-trip coordination cost]] | outcome | 1 |
| [[entities/linearizable-push-ordering|Linearizable push ordering]] | outcome | 2 |
| [[entities/protection-against-permanent-data-loss|Protection against permanent data loss]] | outcome | 1 |
| [[entities/reference-update-amplification|Reference-update amplification]] | outcome | 1 |
| [[entities/replica-latency-update-rate-constraint|Replica-latency update-rate constraint]] | outcome | 2 |
| [[entities/write-unavailability-during-insufficient-replication|Write unavailability during insufficient replication]] | outcome | 2 |

## Relations

- constrains → [[concepts/repository-replica-placement|Repository Replica Placement]]: Durability and publication mechanisms constrain the consistency guarantees that can be offered for accepted pushes.
- consequence → [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]: Choosing standard local Git storage enables reuse of upstream Git behavior and reduces specialized implementation requirements.
- consequence → [[concepts/repository-replica-placement|Repository Replica Placement]]: Write commit and persistence choices determine when replicated topology can expose a consistent repository state.
- ← constrains from [[concepts/repository-replica-placement|Repository Replica Placement]]
- ← co_occurring from [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]

## Evidence

63 open codes from 18 passages in 4 sources.

**Core dimension:** yes ★ (4 sources, 4 systems; core = ≥ 2 sources or ≥ 2 systems).
