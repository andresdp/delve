---
title: Microsoft Scalar
type: system
code: MS-SCALAR
organization: Microsoft
dimensions: 4
tags:
- system
---

# Microsoft Scalar

Client-side configuration of upstream Git features: partial clone, sparse-checkout, background maintenance.

Values supported by passages whose primary system is `MS-SCALAR` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]] | • [[entities/gvfs-protocol-integration|GVFS protocol integration]] (6)<br>• [[entities/sparse-checkout-working-tree|Sparse-checkout working tree]] (6)<br>• [[entities/background-git-object-database-maintenance|Background Git object-database maintenance]] (5)<br>• [[entities/background-commit-graph-maintenance|Background commit-graph maintenance]] (5)<br>• [[entities/built-in-filesystem-monitor|Built-in filesystem monitor]] (4)<br>• [[entities/partial-clone|Partial clone]] (3)<br>• [[entities/user-suspendable-background-maintenance|User-suspendable background maintenance]] (3)<br>• [[entities/watchman-based-filesystem-watching|Watchman-based filesystem watching]] (3)<br>• [[entities/compressed-git-index|Compressed Git index]] (2)<br>• [[entities/default-sparse-clone-initialization|Default sparse clone initialization]] (2)<br>• [[entities/gvfs-protocol-standardization|GVFS protocol standardization]] (2)<br>• [[entities/git-aware-custom-filesystem-watcher|Git-aware custom filesystem watcher]] (2)<br>• [[entities/hourly-background-fetch|Hourly background fetch]] (2)<br>• [[entities/incremental-reachable-commit-graph|Incremental reachable-commit graph]] (2)<br>• [[entities/multi-pack-index-pack-migration|Multi-pack-index pack migration]] (2)<br>• [[entities/virtualized-filesystem-working-tree-scaling|Virtualized filesystem working-tree scaling]] (2)<br>• [[entities/ahead-behind-calculation-suppression|Ahead/behind calculation suppression]] (1)<br>• [[entities/deferred-obsolete-pack-deletion|Deferred obsolete-pack deletion]] (1)<br>• [[entities/gvfs-deployment-without-cache-infrastructure|GVFS deployment without cache infrastructure]] (1)<br>• [[entities/git-untracked-cache|Git untracked cache]] (1)<br>• [[entities/git-protocol-scalar-registration|Git-protocol Scalar registration]] (1)<br>• [[entities/incremental-bounded-pack-repacking|Incremental bounded pack repacking]] (1)<br>• [[entities/local-git-configuration-setup|Local Git configuration setup]] (1)<br>• [[entities/non-virtualized-large-repository-support|Non-virtualized large-repository support]] (1)<br>• [[entities/on-demand-object-retrieval|On-demand object retrieval]] (1)<br>• [[entities/single-file-index-management|Single-file index management]] (1)<br>• [[entities/single-pack-full-repacking|Single-pack full repacking]] (1)<br>• [[entities/small-pack-batch-selection|Small-pack batch selection]] (1)<br>• [[entities/trace-driven-bottleneck-identification|Trace-driven bottleneck identification]] (1)<br>• [[entities/two-phase-repack-and-expire|Two-phase repack and expire]] (1) |
| [[concepts/replica-topology-and-persistence|Replica Topology and Persistence]] | • [[entities/on-demand-repository-materialization|On-demand repository materialization]] (1) |
| [[concepts/repository-service-scaling|Repository Service Scaling]] | • [[entities/automatic-git-performance-configuration|Automatic Git performance configuration]] (5)<br>• [[entities/core-git-upstreaming|Core Git upstreaming]] (4)<br>• [[entities/transitional-scalar-performance-layer|Transitional Scalar performance layer]] (4)<br>• [[entities/explicit-repository-registration|Explicit repository registration]] (3)<br>• [[entities/scalar-local-performance-implementation|Scalar-local performance implementation]] (3)<br>• [[entities/thin-git-configuration-layer|Thin Git configuration layer]] (3)<br>• [[entities/custom-git-client-dependency|Custom Git client dependency]] (2)<br>• [[entities/separated-repository-and-build-artifact-directories|Separated repository and build-artifact directories]] (2)<br>• [[entities/co-located-transfer-cache-proxy|Co-located transfer cache proxy]] (1)<br>• [[entities/disabled-automatic-garbage-collection|Disabled automatic garbage collection]] (1)<br>• [[entities/foreground-automatic-garbage-collection|Foreground automatic garbage collection]] (1)<br>• [[entities/hidden-remote-reference-namespace|Hidden remote-reference namespace]] (1)<br>• [[entities/sync-aware-replica-selection|Sync-aware replica selection]] (1) |
| [[concepts/repository-storage-representation|Repository Storage Representation]] | • [[entities/delta-compressed-packfile-storage|Delta-compressed packfile storage]] (1) |

## Attested design points

[[designs/p001|P001]]
