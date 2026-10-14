---
title: Replica Topology and Persistence
type: dimension
id: '10'
core: true
values: 31
candidate_values: 27
outcomes: 4
evidence:
  codes: 53
  documents: 22
  sources: 4
relations:
- affects [[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Replica Topology and Persistence

Which replica placement and durable state model maintains repository copies across failures?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/arbitrary-replica-based-read-scaling|Arbitrary replica-based read scaling]] | accepted | 2 |
| [[entities/compacted-data-replica-distribution|Compacted-data replica distribution]] | accepted | 2 |
| [[entities/cross-rack-replica-placement|Cross-rack replica placement]] | accepted | 6 |
| [[entities/disk-repository-warm-cache|Disk repository warm cache]] | accepted | 2 |
| [[entities/etag-validated-replica-freshness|ETag-validated replica freshness]] | accepted | 1 |
| [[entities/elastic-per-repository-replica-allocation|Elastic per-repository replica allocation]] | accepted | 3 |
| [[entities/file-server-content-replication|File-server content replication]] | accepted | 1 |
| [[entities/git-application-level-replication|Git application-level replication]] | accepted | 6 |
| [[entities/low-latency-replica-placement|Low-latency replica placement]] | accepted | 2 |
| [[entities/n-to-n-replica-reconstruction|N-to-N replica reconstruction]] | accepted | 2 |
| [[entities/on-demand-repository-materialization|On-demand repository materialization]] | accepted | 2 |
| [[entities/optimistic-udp-catch-up-gossip|Optimistic UDP catch-up gossip]] | accepted | 1 |
| [[entities/proxy-mediated-repository-replication|Proxy-mediated repository replication]] | accepted | 2 |
| [[entities/read-time-replica-catch-up|Read-time replica catch-up]] | accepted | 1 |
| [[entities/rendezvous-hash-placement-hints|Rendezvous-hash placement hints]] | accepted | 2 |
| [[entities/repository-repair-and-rebalancing|Repository repair and rebalancing]] | accepted | 2 |
| [[entities/s3-express-object-storage-substrate|S3 Express object-storage substrate]] | accepted | 3 |
| [[entities/stateless-repository-placement|Stateless repository placement]] | accepted | 2 |
| [[entities/three-replica-repository-topology|Three-replica repository topology]] | accepted | 9 |
| [[entities/wal-propagated-compaction-state|WAL-propagated compaction state]] | accepted | 2 |
| [[entities/write-ahead-log-repository-persistence|Write-ahead-log repository persistence]] | accepted | 3 |
| [[entities/disk-backed-repository-source-of-truth|Disk-backed repository source of truth]] | mixed | 2 |
| [[entities/incremental-replica-checksum-state|Incremental replica checksum state]] | mixed | 3 |
| [[entities/co-located-filesystem-replica-placement|Co-located filesystem replica placement]] | rejected | 1 |
| [[entities/filesystem-block-level-replication|Filesystem block-level replication]] | rejected | 3 |
| [[entities/relational-reference-database-persistence|Relational reference database persistence]] | rejected | 2 |
| [[entities/single-extra-copy-topology|Single-extra-copy topology]] | rejected | 2 |
| [[entities/durable-highly-available-content-access|Durable highly available content access]] | outcome | 1 |
| [[entities/idle-replica-overhead|Idle-replica overhead]] | outcome | 3 |
| [[entities/monorepo-traffic-capacity-shortfall|Monorepo traffic capacity shortfall]] | outcome | 1 |
| [[entities/pet-repository-operational-burden|Pet-repository operational burden]] | outcome | 2 |

## Relations

How to read them: [[relations|Relations between dimensions]].

### From this dimension

- Choices on this dimension affect the outcomes of [[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]. *S3-backed authoritative state, freshness validation, and elastic replica topology change consistency and write-commitment behavior.*


## Evidence

53 open codes from 22 passages in 4 sources.

**Core dimension:** yes ★ (4 sources, 4 systems; core = ≥ 2 sources or ≥ 2 systems).
