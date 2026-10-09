---
title: Repository Replica Placement
type: dimension
id: '1'
core: true
values: 20
candidate_values: 10
outcomes: 10
evidence:
  codes: 33
  documents: 14
  sources: 3
relations:
- constrains [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]
- constrains [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
---

# Repository Replica Placement

Which physical and geographic arrangement of repository copies supports scale and durability?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/multi-disk-repository-placement|Multi-disk repository placement]] | accepted | 1 |
| [[entities/multi-machine-repository-placement|Multi-machine repository placement]] | accepted | 1 |
| [[entities/multi-rack-repository-replication|Multi-rack repository replication]] | accepted | 2 |
| [[entities/multi-server-repository-replication|Multi-server repository replication]] | accepted | 6 |
| [[entities/on-disk-repository-source-of-truth|On-disk repository source of truth]] | accepted | 1 |
| [[entities/three-replica-repository-placement|Three-replica repository placement]] | accepted | 4 |
| [[entities/unsynchronized-packfile-distribution|Unsynchronized packfile distribution]] | accepted | 2 |
| [[entities/drbd-filesystem-block-replication|DRBD filesystem block replication]] | mixed | 1 |
| [[entities/replica-trimming-for-lightly-used-repositories|Replica trimming for lightly used repositories]] | mixed | 2 |
| [[entities/http-daemon-over-on-disk-repository|HTTP daemon over on-disk repository]] | rejected | 1 |
| [[entities/distributed-model-hosting-burden|Distributed-model hosting burden]] | outcome | 1 |
| [[entities/durable-highly-available-repository-access|Durable highly available repository access]] | outcome | 1 |
| [[entities/full-replica-state-checksum-overhead|Full replica-state checksum overhead]] | outcome | 1 |
| [[entities/fully-synchronized-replica-state|Fully synchronized replica state]] | outcome | 2 |
| [[entities/linear-read-scaling|Linear read scaling]] | outcome | 1 |
| [[entities/monorepo-capacity-shortfall|Monorepo capacity shortfall]] | outcome | 1 |
| [[entities/packfile-centered-scalability-ceiling|Packfile-centered scalability ceiling]] | outcome | 1 |
| [[entities/replica-consistency-complexity-cost|Replica-consistency complexity cost]] | outcome | 1 |
| [[entities/replica-count-floor-ceiling-mismatch|Replica-count floor-ceiling mismatch]] | outcome | 1 |
| [[entities/replica-count-scalability-ceiling|Replica-count scalability ceiling]] | outcome | 1 |

## Relations

- constrains → [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]: Quorum and replica-agreement choices determine how many servers can be unavailable during maintenance or failure while preserving writes and reads.
- constrains → [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]: Replica coordination determines whether repository persistence and publication can be implemented through synchronized replicas or a separately durable ingestion log.
- ← constrains from [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]
- ← consequence from [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]
- ← consequence from [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]

## Evidence

33 open codes from 14 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
