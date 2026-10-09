---
title: Cursor Continuity and Origin
type: system
code: CUR-CONT
organization: Cursor
dimensions: 4
tags:
- system
---

# Cursor Continuity and Origin

Write-ahead log in S3 as the source of truth, repositories on disk as a warm cache.

Values supported by passages whose primary system is `CUR-CONT` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]] | • [[entities/continuous-infrastructure-evolution|Continuous infrastructure evolution]] (1)<br>• [[entities/forked-git-implementation|Forked Git implementation]] (1)<br>• [[entities/internal-to-customer-platform-reuse|Internal-to-customer platform reuse]] (1)<br>• [[entities/painless-migration-path|Painless migration path]] (1)<br>• [[entities/proven-engineering-and-operational-philosophy|Proven engineering and operational philosophy]] (1)<br>• [[entities/reliability-performance-and-scale-oriented-hosting-platform|Reliability-, performance-, and scale-oriented hosting platform]] (1) |
| [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]] | • [[entities/arbitrary-replica-read-scale-out|Arbitrary replica read scale-out]] (1) |
| [[concepts/repository-replica-placement|Repository Replica Placement]] | • [[entities/unsynchronized-packfile-distribution|Unsynchronized packfile distribution]] (1) |
| [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]] | • [[entities/replicated-compaction-output|Replicated compaction output]] (2)<br>• [[entities/s3-express-one-zone-wal-storage|S3 Express One Zone WAL storage]] (2)<br>• [[entities/s3-compatible-write-ahead-log|S3-compatible write-ahead log]] (2)<br>• [[entities/wal-first-storage-architecture|WAL-first storage architecture]] (2)<br>• [[entities/batched-wal-persistence|Batched WAL persistence]] (1)<br>• [[entities/durability-before-acknowledgment|Durability-before-acknowledgment]] (1)<br>• [[entities/fully-consistent-replica-synchronization|Fully consistent replica synchronization]] (1)<br>• [[entities/incremental-geometric-repository-compaction|Incremental geometric repository compaction]] (1)<br>• [[entities/local-nvme-git-repository|Local NVMe Git repository]] (1)<br>• [[entities/periodic-repository-compaction|Periodic repository compaction]] (1)<br>• [[entities/primary-only-repository-compaction|Primary-only repository compaction]] (1)<br>• [[entities/reference-transaction-publication-gate|Reference-transaction publication gate]] (1)<br>• [[entities/replica-local-repository-repacking|Replica-local repository repacking]] (1)<br>• [[entities/single-object-write-per-push|Single-object write per push]] (1)<br>• [[entities/wal-propagated-compaction-events|WAL-propagated compaction events]] (1) |

## Attested design points

[[designs/p012|P012]], [[designs/p022|P022]]
