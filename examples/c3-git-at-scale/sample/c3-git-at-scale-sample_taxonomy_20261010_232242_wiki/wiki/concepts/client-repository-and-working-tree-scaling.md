---
title: Client Repository and Working-Tree Scaling
type: dimension
id: '12'
core: true
values: 45
candidate_values: 31
outcomes: 14
evidence:
  codes: 83
  documents: 19
  sources: 4
relations:
- requires [[concepts/repository-storage-representation|Repository Storage Representation]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Client Repository and Working-Tree Scaling

Which client-side clone, index, filesystem-monitoring, checkout, and local maintenance mechanisms scale large repositories?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/ahead-behind-calculation-suppression|Ahead/behind calculation suppression]] | accepted | 1 |
| [[entities/background-git-object-database-maintenance|Background Git object-database maintenance]] | accepted | 6 |
| [[entities/background-commit-graph-maintenance|Background commit-graph maintenance]] | accepted | 5 |
| [[entities/built-in-filesystem-monitor|Built-in filesystem monitor]] | accepted | 4 |
| [[entities/compressed-git-index|Compressed Git index]] | accepted | 2 |
| [[entities/default-sparse-clone-initialization|Default sparse clone initialization]] | accepted | 3 |
| [[entities/deferred-obsolete-pack-deletion|Deferred obsolete-pack deletion]] | accepted | 1 |
| [[entities/gvfs-protocol-integration|GVFS protocol integration]] | accepted | 6 |
| [[entities/git-untracked-cache|Git untracked cache]] | accepted | 1 |
| [[entities/git-protocol-scalar-registration|Git-protocol Scalar registration]] | accepted | 1 |
| [[entities/hourly-background-fetch|Hourly background fetch]] | accepted | 2 |
| [[entities/incremental-bounded-pack-repacking|Incremental bounded pack repacking]] | accepted | 1 |
| [[entities/incremental-reachable-commit-graph|Incremental reachable-commit graph]] | accepted | 2 |
| [[entities/local-git-configuration-setup|Local Git configuration setup]] | accepted | 1 |
| [[entities/multi-pack-index-pack-migration|Multi-pack-index pack migration]] | accepted | 2 |
| [[entities/non-virtualized-large-repository-support|Non-virtualized large-repository support]] | accepted | 1 |
| [[entities/on-demand-object-retrieval|On-demand object retrieval]] | accepted | 2 |
| [[entities/partial-clone|Partial clone]] | accepted | 3 |
| [[entities/rails-monolith|Rails monolith]] | accepted | 2 |
| [[entities/single-file-index-management|Single-file index management]] | accepted | 1 |
| [[entities/small-pack-batch-selection|Small-pack batch selection]] | accepted | 1 |
| [[entities/sparse-checkout-working-tree|Sparse-checkout working tree]] | accepted | 7 |
| [[entities/trace-driven-bottleneck-identification|Trace-driven bottleneck identification]] | accepted | 1 |
| [[entities/two-phase-repack-and-expire|Two-phase repack and expire]] | accepted | 1 |
| [[entities/user-suspendable-background-maintenance|User-suspendable background maintenance]] | accepted | 3 |
| [[entities/gvfs-deployment-without-cache-infrastructure|GVFS deployment without cache infrastructure]] | mixed | 1 |
| [[entities/gvfs-protocol-standardization|GVFS protocol standardization]] | mixed | 3 |
| [[entities/git-aware-custom-filesystem-watcher|Git-aware custom filesystem watcher]] | mixed | 2 |
| [[entities/virtualized-filesystem-working-tree-scaling|Virtualized filesystem working-tree scaling]] | mixed | 2 |
| [[entities/watchman-based-filesystem-watching|Watchman-based filesystem watching]] | mixed | 3 |
| [[entities/single-pack-full-repacking|Single-pack full repacking]] | rejected | 1 |
| [[entities/compatibility-limited-advanced-feature-defaults|Compatibility-limited advanced-feature defaults]] | outcome | 2 |
| [[entities/git-status-latency-reduction|Git status latency reduction]] | outcome | 2 |
| [[entities/improved-delta-encoding-efficiency|Improved delta-encoding efficiency]] | outcome | 1 |
| [[entities/insufficient-scale-for-gvfs|Insufficient scale for GVFS]] | outcome | 1 |
| [[entities/interrupted-clone-progress-loss|Interrupted clone progress loss]] | outcome | 1 |
| [[entities/linux-support|Linux support]] | outcome | 1 |
| [[entities/low-per-entry-index-processing-cost|Low per-entry index processing cost]] | outcome | 1 |
| [[entities/pack-file-handle-pressure|Pack-file handle pressure]] | outcome | 1 |
| [[entities/per-pack-index-scanning-overhead|Per-pack index scanning overhead]] | outcome | 1 |
| [[entities/populated-file-modification-detection-cost|Populated-file modification detection cost]] | outcome | 2 |
| [[entities/reduced-index-storage-footprint|Reduced index storage footprint]] | outcome | 1 |
| [[entities/reduced-initial-clone-footprint|Reduced initial clone footprint]] | outcome | 1 |
| [[entities/selective-modified-path-inspection|Selective modified-path inspection]] | outcome | 1 |
| [[entities/single-pack-equivalent-object-lookup|Single-pack-equivalent object lookup]] | outcome | 1 |

## Relations

How to read them: [[relations|Relations between dimensions]].

### From this dimension

- This dimension requires [[concepts/repository-storage-representation|Repository Storage Representation]] to be decided first. *Client clone, index, and maintenance mechanisms depend on the repository representation exposed to clients.*


## Evidence

83 open codes from 19 passages in 4 sources.

**Core dimension:** yes ★ (4 sources, 4 systems; core = ≥ 2 sources or ≥ 2 systems).
