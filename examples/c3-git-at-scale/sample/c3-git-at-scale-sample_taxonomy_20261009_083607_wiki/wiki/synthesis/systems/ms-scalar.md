---
title: Microsoft Scalar
type: system
code: MS-SCALAR
organization: Microsoft
dimensions: 3
tags:
- system
---

# Microsoft Scalar

Client-side configuration of upstream Git features: partial clone, sparse-checkout, background maintenance.

Values supported by passages whose primary system is `MS-SCALAR` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]] | • [[entities/automatic-commit-graph-and-multi-pack-maintenance|Automatic commit-graph and multi-pack maintenance]] (7)<br>• [[entities/background-repository-maintenance|Background repository maintenance]] (5)<br>• [[entities/sparse-checkout|Sparse checkout]] (4)<br>• [[entities/built-in-file-system-monitor|Built-in file system monitor]] (3)<br>• [[entities/foreground-automatic-garbage-collection|Foreground automatic garbage collection]] (3)<br>• [[entities/partial-clone|Partial clone]] (3)<br>• [[entities/watchman-based-filesystem-watcher|Watchman-based filesystem watcher]] (3)<br>• [[entities/git-aware-filesystem-watcher|Git-aware filesystem watcher]] (2)<br>• [[entities/hourly-background-fetches|Hourly background fetches]] (2)<br>• [[entities/incremental-repository-maintenance|Incremental repository maintenance]] (2)<br>• [[entities/loose-object-and-delta-packed-maintenance|Loose-object and delta-packed maintenance]] (2)<br>• [[entities/single-pack-file-repacking|Single-pack-file repacking]] (2)<br>• [[entities/source-repository-placement-under-src|Source repository placement under /src]] (2)<br>• [[entities/background-garbage-collection-delegation|Background garbage-collection delegation]] (1)<br>• [[entities/combined-repository-maintenance-command|Combined repository maintenance command]] (1)<br>• [[entities/compressed-git-index|Compressed Git index]] (1)<br>• [[entities/disabled-automatic-garbage-collection|Disabled automatic garbage collection]] (1)<br>• [[entities/foreground-maintenance-execution|Foreground maintenance execution]] (1)<br>• [[entities/full-repository-rewrite-garbage-collection|Full repository rewrite garbage collection]] (1)<br>• [[entities/gvfs-object-transfer-protocol|GVFS object-transfer protocol]] (1)<br>• [[entities/hidden-reference-background-fetch|Hidden-reference background fetch]] (1)<br>• [[entities/suppressed-ahead-behind-status-calculation|Suppressed ahead-behind status calculation]] (1)<br>• [[entities/virtualized-filesystem-population|Virtualized filesystem population]] (1) |
| [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]] | • [[entities/gvfs-protocol-support-in-scalar|GVFS protocol support in Scalar]] (3)<br>• [[entities/upstream-contribution-to-core-git|Upstream contribution to core Git]] (3)<br>• [[entities/core-git-eventual-performance-path|Core Git eventual performance path]] (2)<br>• [[entities/custom-git-client-dependency|Custom Git client dependency]] (2)<br>• [[entities/explicit-repository-registration|Explicit repository registration]] (2)<br>• [[entities/local-git-configuration-setup|Local Git configuration setup]] (2)<br>• [[entities/scalar-interim-performance-layer|Scalar interim performance layer]] (2)<br>• [[entities/user-controlled-maintenance-suspension|User-controlled maintenance suspension]] (2)<br>• [[entities/automatic-git-performance-configuration|Automatic Git performance configuration]] (1)<br>• [[entities/background-repository-configuration-updates|Background repository configuration updates]] (1)<br>• [[entities/co-located-gvfs-cache-infrastructure|Co-located GVFS cache infrastructure]] (1)<br>• [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]] (1)<br>• [[entities/git-feature-contributions-replacing-management-layers|Git feature contributions replacing management layers]] (1)<br>• [[entities/git-protocol-without-gvfs-cache-infrastructure|Git protocol without GVFS cache infrastructure]] (1)<br>• [[entities/native-git-repository-integration|Native Git repository integration]] (1)<br>• [[entities/packfile-level-repository-distribution|Packfile-level repository distribution]] (1)<br>• [[entities/reduced-scalar-scope|Reduced Scalar scope]] (1)<br>• [[entities/separate-fetch-objects-service-endpoint|Separate fetch-objects service endpoint]] (1)<br>• [[entities/service-independent-acceleration|Service-independent acceleration]] (1) |
| [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]] | • [[entities/incremental-geometric-repository-compaction|Incremental geometric repository compaction]] (2) |

## Attested design points

[[designs/p001|P001]]
