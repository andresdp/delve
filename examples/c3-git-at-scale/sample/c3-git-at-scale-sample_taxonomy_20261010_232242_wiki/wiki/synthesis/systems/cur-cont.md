---
title: Cursor Continuity and Origin
type: system
code: CUR-CONT
organization: Cursor
dimensions: 5
tags:
- system
---

# Cursor Continuity and Origin

Write-ahead log in S3 as the source of truth, repositories on disk as a warm cache.

Values supported by passages whose primary system is `CUR-CONT` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]] | • [[entities/background-git-object-database-maintenance|Background Git object-database maintenance]] (1) |
| [[concepts/replica-topology-and-persistence|Replica Topology and Persistence]] | • [[entities/s3-express-object-storage-substrate|S3 Express object-storage substrate]] (3)<br>• [[entities/write-ahead-log-repository-persistence|Write-ahead-log repository persistence]] (3)<br>• [[entities/elastic-per-repository-replica-allocation|Elastic per-repository replica allocation]] (2)<br>• [[entities/relational-reference-database-persistence|Relational reference database persistence]] (2)<br>• [[entities/wal-propagated-compaction-state|WAL-propagated compaction state]] (2)<br>• [[entities/arbitrary-replica-based-read-scaling|Arbitrary replica-based read scaling]] (1)<br>• [[entities/compacted-data-replica-distribution|Compacted-data replica distribution]] (1)<br>• [[entities/disk-repository-warm-cache|Disk repository warm cache]] (1)<br>• [[entities/disk-backed-repository-source-of-truth|Disk-backed repository source of truth]] (1)<br>• [[entities/etag-validated-replica-freshness|ETag-validated replica freshness]] (1)<br>• [[entities/n-to-n-replica-reconstruction|N-to-N replica reconstruction]] (1)<br>• [[entities/on-demand-repository-materialization|On-demand repository materialization]] (1)<br>• [[entities/optimistic-udp-catch-up-gossip|Optimistic UDP catch-up gossip]] (1)<br>• [[entities/read-time-replica-catch-up|Read-time replica catch-up]] (1)<br>• [[entities/rendezvous-hash-placement-hints|Rendezvous-hash placement hints]] (1)<br>• [[entities/stateless-repository-placement|Stateless repository placement]] (1) |
| [[concepts/repository-service-scaling|Repository Service Scaling]] | • [[entities/external-repository-placement-routing-table|External repository-placement routing table]] (3)<br>• [[entities/unified-repository-and-wal-compaction|Unified repository and WAL compaction]] (3)<br>• [[entities/batched-object-storage-write-processing|Batched object-storage write processing]] (1)<br>• [[entities/bookkeeping-update-transaction-coalescing|Bookkeeping-update transaction coalescing]] (1)<br>• [[entities/co-located-transfer-cache-proxy|Co-located transfer cache proxy]] (1)<br>• [[entities/evolvable-repository-platform|Evolvable repository platform]] (1)<br>• [[entities/migration-friendly-repository-platform|Migration-friendly repository platform]] (1)<br>• [[entities/periodic-repository-compaction|Periodic repository compaction]] (1)<br>• [[entities/primary-only-repository-compaction|Primary-only repository compaction]] (1)<br>• [[entities/replica-side-repository-repacking|Replica-side repository repacking]] (1)<br>• [[entities/repository-hosting-performance-and-scale-objective|Repository hosting performance and scale objective]] (1)<br>• [[entities/repository-hosting-reliability-objective|Repository hosting reliability objective]] (1)<br>• [[entities/s3-distributed-compacted-packs|S3-distributed compacted packs]] (1) |
| [[concepts/repository-storage-representation|Repository Storage Representation]] | • [[entities/centralized-repository-hosting|Centralized repository hosting]] (1)<br>• [[entities/plain-git-repositories-on-local-nvme|Plain Git repositories on local NVMe]] (1) |
| [[concepts/write-commitment-and-consistency|Write Commitment and Consistency]] | • [[entities/linearized-repository-operations|Linearized repository operations]] (4)<br>• [[entities/wal-durability-before-push-acknowledgement|WAL durability before push acknowledgement]] (3)<br>• [[entities/operation-history-replica-rewind|Operation-history replica rewind]] (2)<br>• [[entities/consensus-free-arbitrary-repository-primaries|Consensus-free arbitrary repository primaries]] (1)<br>• [[entities/eventual-replica-consistency|Eventual replica consistency]] (1)<br>• [[entities/quorum-free-local-publication|Quorum-free local publication]] (1)<br>• [[entities/rendezvous-ranked-primary-preference|Rendezvous-ranked primary preference]] (1)<br>• [[entities/wal-index-publication-ordering|WAL-index publication ordering]] (1) |

## Attested design points

[[designs/p012|P012]], [[designs/p022|P022]]
