---
title: Client Repository Workload Scaling
type: dimension
id: '4'
core: true
values: 38
candidate_values: 25
outcomes: 13
evidence:
  codes: 71
  documents: 17
  sources: 3
relations:
- precondition [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]
- constrains [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Client Repository Workload Scaling

How should clients reduce repository data, working-tree size, metadata work, and command latency at large scale?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/automatic-commit-graph-and-multi-pack-maintenance|Automatic commit-graph and multi-pack maintenance]] | accepted | 7 |
| [[entities/background-garbage-collection-delegation|Background garbage-collection delegation]] | accepted | 1 |
| [[entities/background-repository-maintenance|Background repository maintenance]] | accepted | 5 |
| [[entities/built-in-file-system-monitor|Built-in file system monitor]] | accepted | 3 |
| [[entities/central-server-on-demand-object-retrieval|Central-server on-demand object retrieval]] | accepted | 1 |
| [[entities/combined-repository-maintenance-command|Combined repository maintenance command]] | accepted | 1 |
| [[entities/compressed-git-index|Compressed Git index]] | accepted | 1 |
| [[entities/dag-dependent-repository-traversal|DAG-dependent repository traversal]] | accepted | 1 |
| [[entities/foreground-maintenance-execution|Foreground maintenance execution]] | accepted | 1 |
| [[entities/gvfs-object-transfer-protocol|GVFS object-transfer protocol]] | accepted | 2 |
| [[entities/git-aware-filesystem-watcher|Git-aware filesystem watcher]] | accepted | 2 |
| [[entities/hidden-reference-background-fetch|Hidden-reference background fetch]] | accepted | 1 |
| [[entities/hourly-background-fetches|Hourly background fetches]] | accepted | 2 |
| [[entities/incremental-repository-maintenance|Incremental repository maintenance]] | accepted | 2 |
| [[entities/loose-object-and-delta-packed-maintenance|Loose-object and delta-packed maintenance]] | accepted | 2 |
| [[entities/partial-clone|Partial clone]] | accepted | 3 |
| [[entities/source-repository-placement-under-src|Source repository placement under /src]] | accepted | 2 |
| [[entities/sparse-checkout|Sparse checkout]] | accepted | 5 |
| [[entities/suppressed-ahead-behind-status-calculation|Suppressed ahead-behind status calculation]] | accepted | 1 |
| [[entities/foreground-automatic-garbage-collection|Foreground automatic garbage collection]] | mixed | 3 |
| [[entities/single-pack-file-repacking|Single-pack-file repacking]] | mixed | 2 |
| [[entities/watchman-based-filesystem-watcher|Watchman-based filesystem watcher]] | mixed | 3 |
| [[entities/disabled-automatic-garbage-collection|Disabled automatic garbage collection]] | rejected | 1 |
| [[entities/full-repository-rewrite-garbage-collection|Full repository rewrite garbage collection]] | rejected | 1 |
| [[entities/virtualized-filesystem-population|Virtualized filesystem population]] | rejected | 1 |
| [[entities/client-compatible-clone-efficiency|Client-compatible clone efficiency]] | outcome | 1 |
| [[entities/commit-graph-performance-benefit|Commit-graph performance benefit]] | outcome | 1 |
| [[entities/distributed-store-traversal-round-trips|Distributed-store traversal round trips]] | outcome | 1 |
| [[entities/externalized-build-output|Externalized build output]] | outcome | 1 |
| [[entities/foreground-fetch-commit-graph-overhead|Foreground-fetch commit-graph overhead]] | outcome | 1 |
| [[entities/git-on-disk-compaction-bottleneck|Git on-disk compaction bottleneck]] | outcome | 1 |
| [[entities/high-populated-file-processing-cost|High populated-file processing cost]] | outcome | 1 |
| [[entities/interactive-command-blocking|Interactive command blocking]] | outcome | 1 |
| [[entities/loose-object-storage-overhead|Loose-object storage overhead]] | outcome | 1 |
| [[entities/pack-count-and-storage-reduction|Pack-count and storage reduction]] | outcome | 1 |
| [[entities/pack-index-accumulation-overhead|Pack-index accumulation overhead]] | outcome | 1 |
| [[entities/poor-clone-performance|Poor clone performance]] | outcome | 1 |
| [[entities/system-wide-resource-exhaustion|System-wide resource exhaustion]] | outcome | 1 |

## Relations

- precondition → [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]: Client-scale features require repository activation and configuration through the supporting acceleration tooling.
- constrains → [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]: Long-running client operations make server maintenance choices consequential because interrupted clones can lose substantial progress.
- ← consequence from [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]
- ← consequence from [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]

## Evidence

71 open codes from 17 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 3 systems; core = ≥ 2 sources or ≥ 2 systems).
