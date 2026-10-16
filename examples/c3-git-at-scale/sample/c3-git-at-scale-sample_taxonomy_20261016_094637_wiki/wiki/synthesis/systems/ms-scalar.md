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

Values adopted by passages whose primary system is `MS-SCALAR` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]] ⚠ | • [[entities/background-client-maintenance|Background client maintenance]] (7)<br>• [[entities/scalar-interim-performance-layer|Scalar interim performance layer]] (6)<br>• [[entities/native-git-scalability-improvements|Native Git scalability improvements]] (5)<br>• [[entities/background-split-commit-graph-maintenance|Background split commit-graph maintenance]] (4)<br>• [[entities/integrated-client-optimization-configuration|Integrated client optimization configuration]] (4)<br>• [[entities/automatic-repository-registration|Automatic repository registration]] (3)<br>• [[entities/core-git-capability-consolidation|Core Git capability consolidation]] (3)<br>• [[entities/parallel-checkout-processing|Parallel checkout processing]] (3)<br>• [[entities/git-integrated-filesystem-watching|Git-integrated filesystem watching]] (2)<br>• [[entities/hourly-background-repository-fetch|Hourly background repository fetch]] (2)<br>• [[entities/preserved-visible-branch-references-during-background-fetch|Preserved visible branch references during background fetch]] (2)<br>• [[entities/reachability-based-commit-graph-coverage|Reachability-based commit-graph coverage]] (2)<br>• [[entities/repository-performance-tracing|Repository performance tracing]] (2)<br>• [[entities/working-directory-inspection-by-core-commands|Working-directory inspection by core commands]] (2)<br>• [[entities/complete-tracked-path-index|Complete tracked-path index]] (1)<br>• [[entities/consolidated-client-maintenance-command|Consolidated client maintenance command]] (1)<br>• [[entities/custom-git-client-extensions|Custom Git client extensions]] (1)<br>• [[entities/hidden-remote-reference-namespace|Hidden remote-reference namespace]] (1)<br>• [[entities/persistent-scalar-dependency|Persistent Scalar dependency]] (1)<br>• [[entities/single-file-index-stream-i-o|Single-file index stream I/O]] (1)<br>• [[entities/untracked-cache|Untracked cache]] (1)<br>• [[entities/updated-large-index-file-format|Updated large-index file format]] (1)<br>• [[entities/virtualized-filesystem-client|Virtualized filesystem client]] (1) | • [[entities/foreground-garbage-collection|Foreground garbage collection]] (2)<br>• [[entities/persistent-scalar-dependency|Persistent Scalar dependency]] (1)<br>• [[entities/virtualized-filesystem-client|Virtualized filesystem client]] (1) |
| [[concepts/compaction-maintenance-technique|Compaction Maintenance Technique]] ⚠ | • [[entities/background-incremental-maintenance|Background incremental maintenance]] (7)<br>• [[entities/loose-object-cleanup|Loose-object cleanup]] (1) | • [[entities/single-pack-full-repacking|Single-pack full repacking]] (1) |
| [[concepts/large-repository-object-acquisition|Large-Repository Object Acquisition]] ⚠ | • [[entities/gvfs-demand-driven-transfer|GVFS demand-driven transfer]] (6)<br>• [[entities/standard-git-gvfs-protocol-support|Standard-Git GVFS protocol support]] (4)<br>• [[entities/gvfs-style-object-download-cache-servers|GVFS-style object-download cache servers]] (2)<br>• [[entities/partial-clone-transfer|Partial clone transfer]] (2)<br>• [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]] (1)<br>• [[entities/packfile-based-git-networking|Packfile-based Git networking]] (1) | • [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]] (1)<br>• [[entities/standard-git-gvfs-protocol-support|Standard-Git GVFS protocol support]] (1) |

## Attested design points

[[designs/p009|P009]], [[designs/p016|P016]]
