---
type: System
title: GitHub Spokes
description: Plain Git repositories replicated across servers with three-phase commit on reference updates.
code: GH-SPOKES
organization: GitHub
dimensions: 5
tags:
- system
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# GitHub Spokes

Plain Git repositories replicated across servers with three-phase commit on reference updates.

Values adopted by passages whose primary system is `GH-SPOKES` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [Replica State Comparison](/concepts/replica-state-comparison.md) ⚠ | • [Full checksum recomputation](/entities/full-checksum-recomputation.md) (2)<br>• [Checksum-based replica state comparison](/entities/checksum-based-replica-state-comparison.md) (1)<br>• [Incremental XOR checksum maintenance](/entities/incremental-xor-checksum-maintenance.md) (1) | • [Full checksum recomputation](/entities/full-checksum-recomputation.md) (1) |
| [Replica Synchronization Mechanism](/concepts/replica-synchronization-mechanism.md) ⚠ | • [Spokes repository replication](/entities/spokes-repository-replication.md) (11)<br>• [Git-and-rsync replication](/entities/git-and-rsync-replication.md) (1)<br>• [Packfile-level application replication](/entities/packfile-level-application-replication.md) (1) | • [DRBD block-level replication](/entities/drbd-block-level-replication.md) (2)<br>• [Git-level distribution](/entities/git-level-distribution.md) (1)<br>• [Spokes repository replication](/entities/spokes-repository-replication.md) (1) |
| [Replica Topology](/concepts/replica-topology.md) | • [Three-replica repository replication](/entities/three-replica-repository-replication.md) (8) | • [Single-extra-copy replication](/entities/single-extra-copy-replication.md) (2) |
| [Replica Write Coordination](/concepts/replica-write-coordination.md) ⚠ | • [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) (6)<br>• [Three-phase commit coordination](/entities/three-phase-commit-coordination.md) (4)<br>• [Durability-gated write acceptance](/entities/durability-gated-write-acceptance.md) (2)<br>• [Read-preserving replicated-write optimization](/entities/read-preserving-replicated-write-optimization.md) (2)<br>• [Transactional Git reference updates](/entities/transactional-git-reference-updates.md) (2)<br>• [Consensus-free write acceptance](/entities/consensus-free-write-acceptance.md) (1)<br>• [Consistency-and-partition-tolerance priority](/entities/consistency-and-partition-tolerance-priority.md) (1)<br>• [Orchestrated push fan-out](/entities/orchestrated-push-fan-out.md) (1)<br>• [Overlapped replica-coordination work](/entities/overlapped-replica-coordination-work.md) (1)<br>• [Per-write voting without a primary](/entities/per-write-voting-without-a-primary.md) (1)<br>• [Replica-based distributed locking](/entities/replica-based-distributed-locking.md) (1)<br>• [Rollback of non-majority writes](/entities/rollback-of-non-majority-writes.md) (1)<br>• [Unsynchronized packfile distribution](/entities/unsynchronized-packfile-distribution.md) (1) |  |
| [Repository Placement and Read Routing](/concepts/repository-placement-and-read-routing.md) ⚠ | • [Single-replica read routing](/entities/single-replica-read-routing.md) (3)<br>• [Closest sufficiently fresh replica routing](/entities/closest-sufficiently-fresh-replica-routing.md) (1)<br>• [Explicit repository-location tracking](/entities/explicit-repository-location-tracking.md) (1)<br>• [Rendezvous-hashed repository routing](/entities/rendezvous-hashed-repository-routing.md) (1)<br>• [Stale-routing recovery](/entities/stale-routing-recovery.md) (1) |  |

## Attested design points

[P005](/designs/p005.md), [P011](/designs/p011.md)
