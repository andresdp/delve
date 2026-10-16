---
title: GitHub Spokes
type: system
code: GH-SPOKES
organization: GitHub
dimensions: 5
tags:
- system
---

# GitHub Spokes

Plain Git repositories replicated across servers with three-phase commit on reference updates.

Values adopted by passages whose primary system is `GH-SPOKES` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [[concepts/replica-state-comparison|Replica State Comparison]] ⚠ | • [[entities/full-checksum-recomputation|Full checksum recomputation]] (2)<br>• [[entities/checksum-based-replica-state-comparison|Checksum-based replica state comparison]] (1)<br>• [[entities/incremental-xor-checksum-maintenance|Incremental XOR checksum maintenance]] (1) | • [[entities/full-checksum-recomputation|Full checksum recomputation]] (1) |
| [[concepts/replica-synchronization-mechanism|Replica Synchronization Mechanism]] ⚠ | • [[entities/spokes-repository-replication|Spokes repository replication]] (11)<br>• [[entities/git-and-rsync-replication|Git-and-rsync replication]] (1)<br>• [[entities/packfile-level-application-replication|Packfile-level application replication]] (1) | • [[entities/drbd-block-level-replication|DRBD block-level replication]] (2)<br>• [[entities/git-level-distribution|Git-level distribution]] (1)<br>• [[entities/spokes-repository-replication|Spokes repository replication]] (1) |
| [[concepts/replica-topology|Replica Topology]] | • [[entities/three-replica-repository-replication|Three-replica repository replication]] (8) | • [[entities/single-extra-copy-replication|Single-extra-copy replication]] (2) |
| [[concepts/replica-write-coordination|Replica Write Coordination]] ⚠ | • [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] (6)<br>• [[entities/three-phase-commit-coordination|Three-phase commit coordination]] (4)<br>• [[entities/durability-gated-write-acceptance|Durability-gated write acceptance]] (2)<br>• [[entities/read-preserving-replicated-write-optimization|Read-preserving replicated-write optimization]] (2)<br>• [[entities/transactional-git-reference-updates|Transactional Git reference updates]] (2)<br>• [[entities/consensus-free-write-acceptance|Consensus-free write acceptance]] (1)<br>• [[entities/consistency-and-partition-tolerance-priority|Consistency-and-partition-tolerance priority]] (1)<br>• [[entities/orchestrated-push-fan-out|Orchestrated push fan-out]] (1)<br>• [[entities/overlapped-replica-coordination-work|Overlapped replica-coordination work]] (1)<br>• [[entities/per-write-voting-without-a-primary|Per-write voting without a primary]] (1)<br>• [[entities/replica-based-distributed-locking|Replica-based distributed locking]] (1)<br>• [[entities/rollback-of-non-majority-writes|Rollback of non-majority writes]] (1)<br>• [[entities/unsynchronized-packfile-distribution|Unsynchronized packfile distribution]] (1) |  |
| [[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]] ⚠ | • [[entities/single-replica-read-routing|Single-replica read routing]] (3)<br>• [[entities/closest-sufficiently-fresh-replica-routing|Closest sufficiently fresh replica routing]] (1)<br>• [[entities/explicit-repository-location-tracking|Explicit repository-location tracking]] (1)<br>• [[entities/rendezvous-hashed-repository-routing|Rendezvous-hashed repository routing]] (1)<br>• [[entities/stale-routing-recovery|Stale-routing recovery]] (1) |  |

## Attested design points

[[designs/p005|P005]], [[designs/p011|P011]]
