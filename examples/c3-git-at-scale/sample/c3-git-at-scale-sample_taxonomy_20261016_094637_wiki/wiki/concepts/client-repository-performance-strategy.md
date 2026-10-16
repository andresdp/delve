---
type: Design Decision
title: Client Repository Performance Strategy
description: How client-side Git performance is improved, contrasting integrated configuration and tooling with native Git scalability changes.
id: '9'
core: true
values: 33
candidate_values: 24
outcomes: 9
evidence:
  codes: 76
  documents: 18
  sources: 3
relations: []
tags:
- dimension
- core
exclusivity: 0.0
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/ms-scalar.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Client Repository Performance Strategy

How client-side Git performance is improved, contrasting integrated configuration and tooling with native Git scalability changes.

## Values

| Value | Status | Passages |
|---|---|---|
| [Automatic repository registration](/entities/automatic-repository-registration.md) | accepted | 3 |
| [Background client maintenance](/entities/background-client-maintenance.md) | accepted | 7 |
| [Background split commit-graph maintenance](/entities/background-split-commit-graph-maintenance.md) | accepted | 4 |
| [Complete tracked-path index](/entities/complete-tracked-path-index.md) | accepted | 1 |
| [Consolidated client maintenance command](/entities/consolidated-client-maintenance-command.md) | accepted | 1 |
| [Core Git capability consolidation](/entities/core-git-capability-consolidation.md) | accepted | 4 |
| [Custom Git client extensions](/entities/custom-git-client-extensions.md) | accepted | 1 |
| [Git-integrated filesystem watching](/entities/git-integrated-filesystem-watching.md) | accepted | 2 |
| [Hidden remote-reference namespace](/entities/hidden-remote-reference-namespace.md) | accepted | 1 |
| [Hourly background repository fetch](/entities/hourly-background-repository-fetch.md) | accepted | 2 |
| [Integrated client optimization configuration](/entities/integrated-client-optimization-configuration.md) | accepted | 4 |
| [Native Git scalability improvements](/entities/native-git-scalability-improvements.md) | accepted | 6 |
| [Parallel checkout processing](/entities/parallel-checkout-processing.md) | accepted | 3 |
| [Preserved visible branch references during background fetch](/entities/preserved-visible-branch-references-during-background-fetch.md) | accepted | 2 |
| [Reachability-based commit-graph coverage](/entities/reachability-based-commit-graph-coverage.md) | accepted | 2 |
| [Repository performance tracing](/entities/repository-performance-tracing.md) | accepted | 3 |
| [Scalar interim performance layer](/entities/scalar-interim-performance-layer.md) | accepted | 6 |
| [Single-file index stream I/O](/entities/single-file-index-stream-i-o.md) | accepted | 1 |
| [Untracked cache](/entities/untracked-cache.md) | accepted | 1 |
| [Updated large-index file format](/entities/updated-large-index-file-format.md) | accepted | 1 |
| [Working-directory inspection by core commands](/entities/working-directory-inspection-by-core-commands.md) | accepted | 2 |
| [Persistent Scalar dependency](/entities/persistent-scalar-dependency.md) | mixed | 2 |
| [Virtualized filesystem client](/entities/virtualized-filesystem-client.md) | mixed | 2 |
| [Foreground garbage collection](/entities/foreground-garbage-collection.md) | rejected | 2 |
| [Checkout slowdown after virtualization removal](/entities/checkout-slowdown-after-virtualization-removal.md) | outcome | 2 |
| [Compatibility-driven default-off performance features](/entities/compatibility-driven-default-off-performance-features.md) | outcome | 1 |
| [Foreground maintenance command blocking](/entities/foreground-maintenance-command-blocking.md) | outcome | 3 |
| [Foreground-fetch overhead](/entities/foreground-fetch-overhead.md) | outcome | 1 |
| [Index compression from 400 MB to 250 MB](/entities/index-compression-from-400-mb-to-250-mb.md) | outcome | 1 |
| [Low average index-entry processing time](/entities/low-average-index-entry-processing-time.md) | outcome | 1 |
| [Multi-million-entry index](/entities/multi-million-entry-index.md) | outcome | 1 |
| [Performance decay from deferred cleanup](/entities/performance-decay-from-deferred-cleanup.md) | outcome | 1 |
| [System-wide rewrite resource exhaustion](/entities/system-wide-rewrite-resource-exhaustion.md) | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [Native Git scalability improvements](/entities/native-git-scalability-improvements.md) and [Repository performance tracing](/entities/repository-performance-tracing.md): [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [Native Git scalability improvements](/entities/native-git-scalability-improvements.md) and [Core Git capability consolidation](/entities/core-git-capability-consolidation.md): [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [Repository performance tracing](/entities/repository-performance-tracing.md) and [Core Git capability consolidation](/entities/core-git-capability-consolidation.md): [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [Integrated client optimization configuration](/entities/integrated-client-optimization-configuration.md) and [Native Git scalability improvements](/entities/native-git-scalability-improvements.md): [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [Integrated client optimization configuration](/entities/integrated-client-optimization-configuration.md) and [Repository performance tracing](/entities/repository-performance-tracing.md): [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- 248 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

76 open codes from 18 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
