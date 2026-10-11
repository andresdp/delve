---
title: Write Commitment and Consistency
type: dimension
id: '6'
core: true
values: 41
candidate_values: 31
outcomes: 10
evidence:
  codes: 56
  documents: 21
  sources: 3
relations:
- affects [[concepts/repository-service-scaling|Repository Service Scaling]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
---

# Write Commitment and Consistency

Which consistency, acknowledgment, locking, and refusal policy governs accepting repository writes?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/atomic-reference-update-rollback|Atomic reference-update rollback]] | accepted | 2 |
| [[entities/automatic-replica-repair|Automatic replica repair]] | accepted | 1 |
| [[entities/consensus-free-arbitrary-repository-primaries|Consensus-free arbitrary repository primaries]] | accepted | 1 |
| [[entities/consistency-and-partition-tolerance-priority|Consistency and partition tolerance priority]] | accepted | 1 |
| [[entities/continued-write-replication-during-quiescing|Continued write replication during quiescing]] | accepted | 2 |
| [[entities/deterministic-replica-transaction-results|Deterministic replica transaction results]] | accepted | 1 |
| [[entities/git-reference-update-transactions|Git reference-update transactions]] | accepted | 2 |
| [[entities/linearized-repository-operations|Linearized repository operations]] | accepted | 6 |
| [[entities/majority-exclusive-write-locking|Majority-exclusive write locking]] | accepted | 1 |
| [[entities/minimum-two-replica-commitment|Minimum two-replica commitment]] | accepted | 1 |
| [[entities/non-majority-write-rollback|Non-majority write rollback]] | accepted | 2 |
| [[entities/non-voting-geo-replicated-hosts|Non-voting geo-replicated hosts]] | accepted | 1 |
| [[entities/operation-history-replica-rewind|Operation-history replica rewind]] | accepted | 2 |
| [[entities/overlapped-replica-coordination-work|Overlapped replica coordination work]] | accepted | 1 |
| [[entities/per-write-ordering-election|Per-write ordering election]] | accepted | 1 |
| [[entities/permanent-data-loss-resistance|Permanent data-loss resistance]] | accepted | 1 |
| [[entities/pre-acquired-reference-locks|Pre-acquired reference locks]] | accepted | 2 |
| [[entities/pre-commit-reference-validation|Pre-commit reference validation]] | accepted | 2 |
| [[entities/quorum-based-replica-acceptance|Quorum-based replica acceptance]] | accepted | 4 |
| [[entities/rendezvous-ranked-primary-preference|Rendezvous-ranked primary preference]] | accepted | 1 |
| [[entities/replica-based-distributed-locking|Replica-based distributed locking]] | accepted | 1 |
| [[entities/strict-majority-write-acknowledgment|Strict-majority write acknowledgment]] | accepted | 3 |
| [[entities/synchronous-write-commitment|Synchronous write commitment]] | accepted | 1 |
| [[entities/three-phase-commit-consensus|Three-phase commit consensus]] | accepted | 4 |
| [[entities/unhealthy-replica-exclusion|Unhealthy replica exclusion]] | accepted | 1 |
| [[entities/wal-durability-before-push-acknowledgement|WAL durability before push acknowledgement]] | accepted | 4 |
| [[entities/wal-index-publication-ordering|WAL-index publication ordering]] | accepted | 1 |
| [[entities/write-refusal-under-insufficient-replication|Write refusal under insufficient replication]] | accepted | 1 |
| [[entities/eventual-replica-consistency|Eventual replica consistency]] | mixed | 2 |
| [[entities/quorum-free-local-publication|Quorum-free local publication]] | rejected | 1 |
| [[entities/single-primary-replication-model|Single-primary replication model]] | rejected | 1 |
| [[entities/availability-sacrifice-for-durability|Availability sacrifice for durability]] | outcome | 1 |
| [[entities/compare-and-swap-retry-delay|Compare-and-swap retry delay]] | outcome | 1 |
| [[entities/consensus-tail-latency-growth|Consensus tail-latency growth]] | outcome | 1 |
| [[entities/degraded-correctness-healthy-speed-behavior|Degraded-correctness healthy-speed behavior]] | outcome | 1 |
| [[entities/globally-consistent-replica-reads|Globally consistent replica reads]] | outcome | 2 |
| [[entities/per-repository-reference-update-latency-budget|Per-repository reference-update latency budget]] | outcome | 1 |
| [[entities/push-unavailability-without-quorum|Push unavailability without quorum]] | outcome | 1 |
| [[entities/replica-coordination-round-trip-cost|Replica coordination round-trip cost]] | outcome | 1 |
| [[entities/replica-count-push-throughput-degradation|Replica-count push-throughput degradation]] | outcome | 1 |
| [[entities/replication-consistency-complexity-cost|Replication consistency complexity cost]] | outcome | 1 |

## Relations

How to read them: [[relations|Relations between dimensions]].

### From this dimension

- Choices on this dimension affect the outcomes of [[concepts/repository-service-scaling|Repository Service Scaling]]. *Synchronous commitment, quorum locking, and refusal during insufficient replication can increase write latency or temporary request unavailability.*

### To this dimension

- Choices on [[concepts/repository-storage-representation|Repository Storage Representation]] affect the outcomes of this dimension. *Replica count and placement determine whether quorum or synchronous durability requirements can be met and influence capacity and latency.*
- Choices on [[concepts/replica-topology-and-persistence|Replica Topology and Persistence]] affect the outcomes of this dimension. *S3-backed authoritative state, freshness validation, and elastic replica topology change consistency and write-commitment behavior.*

## Evidence

56 open codes from 21 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
