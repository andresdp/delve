---
title: Replica Write Coordination
type: dimension
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
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
---

# Replica Write Coordination

How are replicated repository writes ordered, committed, and accepted?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/consensus-free-write-acceptance|Consensus-free write acceptance]] | accepted | 3 |
| [[entities/consistency-and-partition-tolerance-priority|Consistency-and-partition-tolerance priority]] | accepted | 1 |
| [[entities/durability-gated-write-acceptance|Durability-gated write acceptance]] | accepted | 2 |
| [[entities/orchestrated-push-fan-out|Orchestrated push fan-out]] | accepted | 1 |
| [[entities/overlapped-replica-coordination-work|Overlapped replica-coordination work]] | accepted | 1 |
| [[entities/per-write-voting-without-a-primary|Per-write voting without a primary]] | accepted | 1 |
| [[entities/read-preserving-replicated-write-optimization|Read-preserving replicated-write optimization]] | accepted | 2 |
| [[entities/replica-based-distributed-locking|Replica-based distributed locking]] | accepted | 1 |
| [[entities/rollback-of-non-majority-writes|Rollback of non-majority writes]] | accepted | 1 |
| [[entities/single-local-repository-synchronization|Single-local-repository synchronization]] | accepted | 1 |
| [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] | accepted | 8 |
| [[entities/three-phase-commit-coordination|Three-phase commit coordination]] | accepted | 4 |
| [[entities/transactional-git-reference-updates|Transactional Git reference updates]] | accepted | 2 |
| [[entities/unsynchronized-packfile-distribution|Unsynchronized packfile distribution]] | accepted | 1 |
| [[entities/reference-update-amplification|Reference-update amplification]] | outcome | 1 |
| [[entities/replica-round-trip-coordination-latency|Replica round-trip coordination latency]] | outcome | 1 |
| [[entities/replica-count-push-throughput-degradation|Replica-count push-throughput degradation]] | outcome | 1 |
| [[entities/replica-distance-reference-update-limit|Replica-distance reference-update limit]] | outcome | 4 |
| [[entities/slowest-replica-consensus-latency|Slowest-replica consensus latency]] | outcome | 1 |
| [[entities/write-unavailability-during-replication-shortfall|Write unavailability during replication shortfall]] | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] and [[entities/consensus-free-write-acceptance|Consensus-free write acceptance]]: [[synthesis/systems/cur-cont|Cursor Continuity and Origin]], [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] and [[entities/three-phase-commit-coordination|Three-phase commit coordination]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] and [[entities/transactional-git-reference-updates|Transactional Git reference updates]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] and [[entities/per-write-voting-without-a-primary|Per-write voting without a primary]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/strict-majority-coordinated-writes|Strict-majority coordinated writes]] and [[entities/rollback-of-non-majority-writes|Rollback of non-majority writes]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- 75 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

38 open codes from 16 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
