---
type: Design Decision
title: Replica Write Coordination
description: How are replicated repository writes ordered, committed, and accepted?
id: '30'
core: true
values: 20
candidate_values: 14
outcomes: 6
evidence:
  codes: 38
  documents: 16
  sources: 3
relations: []
tags:
- dimension
- core
exclusivity: 0.0
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-spokes.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica Write Coordination

How are replicated repository writes ordered, committed, and accepted?

## Values

| Value | Status | Passages |
|---|---|---|
| [Consensus-free write acceptance](/entities/consensus-free-write-acceptance.md) | accepted | 3 |
| [Consistency-and-partition-tolerance priority](/entities/consistency-and-partition-tolerance-priority.md) | accepted | 1 |
| [Durability-gated write acceptance](/entities/durability-gated-write-acceptance.md) | accepted | 2 |
| [Orchestrated push fan-out](/entities/orchestrated-push-fan-out.md) | accepted | 1 |
| [Overlapped replica-coordination work](/entities/overlapped-replica-coordination-work.md) | accepted | 1 |
| [Per-write voting without a primary](/entities/per-write-voting-without-a-primary.md) | accepted | 1 |
| [Read-preserving replicated-write optimization](/entities/read-preserving-replicated-write-optimization.md) | accepted | 2 |
| [Replica-based distributed locking](/entities/replica-based-distributed-locking.md) | accepted | 1 |
| [Rollback of non-majority writes](/entities/rollback-of-non-majority-writes.md) | accepted | 1 |
| [Single-local-repository synchronization](/entities/single-local-repository-synchronization.md) | accepted | 1 |
| [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) | accepted | 8 |
| [Three-phase commit coordination](/entities/three-phase-commit-coordination.md) | accepted | 4 |
| [Transactional Git reference updates](/entities/transactional-git-reference-updates.md) | accepted | 2 |
| [Unsynchronized packfile distribution](/entities/unsynchronized-packfile-distribution.md) | accepted | 1 |
| [Reference-update amplification](/entities/reference-update-amplification.md) | outcome | 1 |
| [Replica round-trip coordination latency](/entities/replica-round-trip-coordination-latency.md) | outcome | 1 |
| [Replica-count push-throughput degradation](/entities/replica-count-push-throughput-degradation.md) | outcome | 1 |
| [Replica-distance reference-update limit](/entities/replica-distance-reference-update-limit.md) | outcome | 4 |
| [Slowest-replica consensus latency](/entities/slowest-replica-consensus-latency.md) | outcome | 1 |
| [Write unavailability during replication shortfall](/entities/write-unavailability-during-replication-shortfall.md) | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) and [Consensus-free write acceptance](/entities/consensus-free-write-acceptance.md): [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md), [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) and [Three-phase commit coordination](/entities/three-phase-commit-coordination.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) and [Transactional Git reference updates](/entities/transactional-git-reference-updates.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) and [Per-write voting without a primary](/entities/per-write-voting-without-a-primary.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) and [Rollback of non-majority writes](/entities/rollback-of-non-majority-writes.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- 75 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

38 open codes from 16 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
