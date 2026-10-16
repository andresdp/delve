---
type: System
title: Microsoft Scalar
description: 'Client-side configuration of upstream Git features: partial clone, sparse-checkout, background maintenance.'
code: MS-SCALAR
organization: Microsoft
dimensions: 3
tags:
- system
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Microsoft Scalar

Client-side configuration of upstream Git features: partial clone, sparse-checkout, background maintenance.

Values adopted by passages whose primary system is `MS-SCALAR` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [Client Repository Performance Strategy](/concepts/client-repository-performance-strategy.md) ⚠ | • [Background client maintenance](/entities/background-client-maintenance.md) (7)<br>• [Scalar interim performance layer](/entities/scalar-interim-performance-layer.md) (6)<br>• [Native Git scalability improvements](/entities/native-git-scalability-improvements.md) (5)<br>• [Background split commit-graph maintenance](/entities/background-split-commit-graph-maintenance.md) (4)<br>• [Integrated client optimization configuration](/entities/integrated-client-optimization-configuration.md) (4)<br>• [Automatic repository registration](/entities/automatic-repository-registration.md) (3)<br>• [Core Git capability consolidation](/entities/core-git-capability-consolidation.md) (3)<br>• [Parallel checkout processing](/entities/parallel-checkout-processing.md) (3)<br>• [Git-integrated filesystem watching](/entities/git-integrated-filesystem-watching.md) (2)<br>• [Hourly background repository fetch](/entities/hourly-background-repository-fetch.md) (2)<br>• [Preserved visible branch references during background fetch](/entities/preserved-visible-branch-references-during-background-fetch.md) (2)<br>• [Reachability-based commit-graph coverage](/entities/reachability-based-commit-graph-coverage.md) (2)<br>• [Repository performance tracing](/entities/repository-performance-tracing.md) (2)<br>• [Working-directory inspection by core commands](/entities/working-directory-inspection-by-core-commands.md) (2)<br>• [Complete tracked-path index](/entities/complete-tracked-path-index.md) (1)<br>• [Consolidated client maintenance command](/entities/consolidated-client-maintenance-command.md) (1)<br>• [Custom Git client extensions](/entities/custom-git-client-extensions.md) (1)<br>• [Hidden remote-reference namespace](/entities/hidden-remote-reference-namespace.md) (1)<br>• [Persistent Scalar dependency](/entities/persistent-scalar-dependency.md) (1)<br>• [Single-file index stream I/O](/entities/single-file-index-stream-i-o.md) (1)<br>• [Untracked cache](/entities/untracked-cache.md) (1)<br>• [Updated large-index file format](/entities/updated-large-index-file-format.md) (1)<br>• [Virtualized filesystem client](/entities/virtualized-filesystem-client.md) (1) | • [Foreground garbage collection](/entities/foreground-garbage-collection.md) (2)<br>• [Persistent Scalar dependency](/entities/persistent-scalar-dependency.md) (1)<br>• [Virtualized filesystem client](/entities/virtualized-filesystem-client.md) (1) |
| [Compaction Maintenance Technique](/concepts/compaction-maintenance-technique.md) ⚠ | • [Background incremental maintenance](/entities/background-incremental-maintenance.md) (7)<br>• [Loose-object cleanup](/entities/loose-object-cleanup.md) (1) | • [Single-pack full repacking](/entities/single-pack-full-repacking.md) (1) |
| [Large-Repository Object Acquisition](/concepts/large-repository-object-acquisition.md) ⚠ | • [GVFS demand-driven transfer](/entities/gvfs-demand-driven-transfer.md) (6)<br>• [Standard-Git GVFS protocol support](/entities/standard-git-gvfs-protocol-support.md) (4)<br>• [GVFS-style object-download cache servers](/entities/gvfs-style-object-download-cache-servers.md) (2)<br>• [Partial clone transfer](/entities/partial-clone-transfer.md) (2)<br>• [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md) (1)<br>• [Packfile-based Git networking](/entities/packfile-based-git-networking.md) (1) | • [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md) (1)<br>• [Standard-Git GVFS protocol support](/entities/standard-git-gvfs-protocol-support.md) (1) |

## Attested design points

[P009](/designs/p009.md), [P016](/designs/p016.md)
