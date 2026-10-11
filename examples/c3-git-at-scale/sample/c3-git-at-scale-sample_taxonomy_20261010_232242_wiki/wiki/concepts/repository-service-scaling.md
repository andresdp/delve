---
title: Repository Service Scaling
type: dimension
id: '11'
core: true
values: 61
candidate_values: 44
outcomes: 17
evidence:
  codes: 96
  documents: 38
  sources: 5
relations:
- requires [[concepts/repository-storage-representation|Repository Storage Representation]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Repository Service Scaling

Which server-side routing, transfer, failure-detection, maintenance, and platform mechanisms scale repository service workloads?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/advisory-replica-deprioritization|Advisory replica deprioritization]] | accepted | 1 |
| [[entities/application-traffic-failure-monitoring|Application-traffic failure monitoring]] | accepted | 2 |
| [[entities/automatic-git-performance-configuration|Automatic Git performance configuration]] | accepted | 5 |
| [[entities/bookkeeping-update-transaction-coalescing|Bookkeeping-update transaction coalescing]] | accepted | 2 |
| [[entities/bounded-concurrent-reboot-count|Bounded concurrent reboot count]] | accepted | 1 |
| [[entities/centralized-missing-object-dependency|Centralized missing-object dependency]] | accepted | 1 |
| [[entities/checksum-guided-repository-repair-scheduling|Checksum-guided repository repair scheduling]] | accepted | 3 |
| [[entities/co-located-transfer-cache-proxy|Co-located transfer cache proxy]] | accepted | 3 |
| [[entities/core-git-upstreaming|Core Git upstreaming]] | accepted | 4 |
| [[entities/custom-git-client-dependency|Custom Git client dependency]] | accepted | 2 |
| [[entities/evolvable-repository-platform|Evolvable repository platform]] | accepted | 1 |
| [[entities/explicit-repository-registration|Explicit repository registration]] | accepted | 3 |
| [[entities/geographically-nearby-read-replicas|Geographically nearby read replicas]] | accepted | 4 |
| [[entities/hidden-remote-reference-namespace|Hidden remote-reference namespace]] | accepted | 1 |
| [[entities/migration-friendly-repository-platform|Migration-friendly repository platform]] | accepted | 1 |
| [[entities/operation-level-replica-failover|Operation-level replica failover]] | accepted | 1 |
| [[entities/per-application-server-failure-detectors|Per-application-server failure detectors]] | accepted | 5 |
| [[entities/periodic-repository-compaction|Periodic repository compaction]] | accepted | 1 |
| [[entities/preference-ordered-replica-routing|Preference-ordered replica routing]] | accepted | 2 |
| [[entities/primary-only-repository-compaction|Primary-only repository compaction]] | accepted | 1 |
| [[entities/priority-scheduling-for-user-updates|Priority scheduling for user updates]] | accepted | 1 |
| [[entities/quiesced-read-admission|Quiesced read admission]] | accepted | 2 |
| [[entities/quiesced-rolling-server-reboot|Quiesced rolling server reboot]] | accepted | 3 |
| [[entities/rpc-failover-pattern-monitoring|RPC failover-pattern monitoring]] | accepted | 1 |
| [[entities/rack-scoped-maintenance-failure-domain|Rack-scoped maintenance failure domain]] | accepted | 3 |
| [[entities/reference-operation-speedups|Reference-operation speedups]] | accepted | 1 |
| [[entities/repository-hosting-performance-and-scale-objective|Repository hosting performance and scale objective]] | accepted | 1 |
| [[entities/repository-hosting-reliability-objective|Repository hosting reliability objective]] | accepted | 1 |
| [[entities/s3-distributed-compacted-packs|S3-distributed compacted packs]] | accepted | 1 |
| [[entities/separated-repository-and-build-artifact-directories|Separated repository and build-artifact directories]] | accepted | 2 |
| [[entities/sync-aware-replica-selection|Sync-aware replica selection]] | accepted | 3 |
| [[entities/thin-git-configuration-layer|Thin Git configuration layer]] | accepted | 3 |
| [[entities/three-failure-offline-threshold|Three-failure offline threshold]] | accepted | 2 |
| [[entities/transitional-scalar-performance-layer|Transitional Scalar performance layer]] | accepted | 4 |
| [[entities/unified-repository-and-wal-compaction|Unified repository and WAL compaction]] | accepted | 3 |
| [[entities/batched-object-storage-write-processing|Batched object-storage write processing]] | mixed | 2 |
| [[entities/external-repository-placement-routing-table|External repository-placement routing table]] | mixed | 5 |
| [[entities/heartbeat-load-polling|Heartbeat load polling]] | mixed | 2 |
| [[entities/replica-removal-after-repeated-failures|Replica removal after repeated failures]] | mixed | 2 |
| [[entities/scalar-local-performance-implementation|Scalar-local performance implementation]] | mixed | 3 |
| [[entities/disabled-automatic-garbage-collection|Disabled automatic garbage collection]] | rejected | 1 |
| [[entities/foreground-automatic-garbage-collection|Foreground automatic garbage collection]] | rejected | 1 |
| [[entities/immediate-server-reboot|Immediate server reboot]] | rejected | 2 |
| [[entities/replica-side-repository-repacking|Replica-side repository repacking]] | rejected | 1 |
| [[entities/agent-driven-repository-workload-growth|Agent-driven repository workload growth]] | outcome | 1 |
| [[entities/bandwidth-for-cpu-compaction-tradeoff|Bandwidth-for-CPU compaction tradeoff]] | outcome | 1 |
| [[entities/compaction-bottleneck|Compaction bottleneck]] | outcome | 1 |
| [[entities/development-productivity-impact-of-repository-downtime|Development productivity impact of repository downtime]] | outcome | 1 |
| [[entities/false-positive-server-removal|False-positive server removal]] | outcome | 1 |
| [[entities/foreground-maintenance-command-blocking|Foreground maintenance command blocking]] | outcome | 2 |
| [[entities/horizontal-repository-service-scalability|Horizontal repository-service scalability]] | outcome | 2 |
| [[entities/hot-repository-availability-and-performance-gaps|Hot-repository availability and performance gaps]] | outcome | 1 |
| [[entities/localized-failure-detection-false-positive|Localized failure-detection false positive]] | outcome | 1 |
| [[entities/no-production-traffic-impact|No production traffic impact]] | outcome | 2 |
| [[entities/packfile-transfer-burden|Packfile transfer burden]] | outcome | 3 |
| [[entities/read-performance-protection-during-write-optimization|Read-performance protection during write optimization]] | outcome | 1 |
| [[entities/reduced-git-transfer-time|Reduced Git transfer time]] | outcome | 1 |
| [[entities/reference-update-processing-delay|Reference-update processing delay]] | outcome | 1 |
| [[entities/repository-performance-decay|Repository performance decay]] | outcome | 1 |
| [[entities/system-wide-maintenance-resource-exhaustion|System-wide maintenance resource exhaustion]] | outcome | 1 |
| [[entities/temporary-reduced-copy-state|Temporary reduced-copy state]] | outcome | 1 |

## Relations

How to read them: [[relations|Relations between dimensions]].

### From this dimension

- This dimension requires [[concepts/repository-storage-representation|Repository Storage Representation]] to be decided first. *Synchronized read routing, replica health decisions, and geo-distributed serving depend on knowing replica locations and topology.*

### To this dimension

- Choices on [[concepts/write-commitment-and-consistency|Write Commitment and Consistency]] affect the outcomes of this dimension. *Synchronous commitment, quorum locking, and refusal during insufficient replication can increase write latency or temporary request unavailability.*

## Evidence

96 open codes from 38 passages in 5 sources.

**Core dimension:** yes ★ (5 sources, 4 systems; core = ≥ 2 sources or ≥ 2 systems).
