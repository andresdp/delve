---
title: Client Repository Performance Strategy
type: dimension
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
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Client Repository Performance Strategy

How client-side Git performance is improved, contrasting integrated configuration and tooling with native Git scalability changes.

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/automatic-repository-registration|Automatic repository registration]] | accepted | 3 |
| [[entities/background-client-maintenance|Background client maintenance]] | accepted | 7 |
| [[entities/background-split-commit-graph-maintenance|Background split commit-graph maintenance]] | accepted | 4 |
| [[entities/complete-tracked-path-index|Complete tracked-path index]] | accepted | 1 |
| [[entities/consolidated-client-maintenance-command|Consolidated client maintenance command]] | accepted | 1 |
| [[entities/core-git-capability-consolidation|Core Git capability consolidation]] | accepted | 4 |
| [[entities/custom-git-client-extensions|Custom Git client extensions]] | accepted | 1 |
| [[entities/git-integrated-filesystem-watching|Git-integrated filesystem watching]] | accepted | 2 |
| [[entities/hidden-remote-reference-namespace|Hidden remote-reference namespace]] | accepted | 1 |
| [[entities/hourly-background-repository-fetch|Hourly background repository fetch]] | accepted | 2 |
| [[entities/integrated-client-optimization-configuration|Integrated client optimization configuration]] | accepted | 4 |
| [[entities/native-git-scalability-improvements|Native Git scalability improvements]] | accepted | 6 |
| [[entities/parallel-checkout-processing|Parallel checkout processing]] | accepted | 3 |
| [[entities/preserved-visible-branch-references-during-background-fetch|Preserved visible branch references during background fetch]] | accepted | 2 |
| [[entities/reachability-based-commit-graph-coverage|Reachability-based commit-graph coverage]] | accepted | 2 |
| [[entities/repository-performance-tracing|Repository performance tracing]] | accepted | 3 |
| [[entities/scalar-interim-performance-layer|Scalar interim performance layer]] | accepted | 6 |
| [[entities/single-file-index-stream-i-o|Single-file index stream I/O]] | accepted | 1 |
| [[entities/untracked-cache|Untracked cache]] | accepted | 1 |
| [[entities/updated-large-index-file-format|Updated large-index file format]] | accepted | 1 |
| [[entities/working-directory-inspection-by-core-commands|Working-directory inspection by core commands]] | accepted | 2 |
| [[entities/persistent-scalar-dependency|Persistent Scalar dependency]] | mixed | 2 |
| [[entities/virtualized-filesystem-client|Virtualized filesystem client]] | mixed | 2 |
| [[entities/foreground-garbage-collection|Foreground garbage collection]] | rejected | 2 |
| [[entities/checkout-slowdown-after-virtualization-removal|Checkout slowdown after virtualization removal]] | outcome | 2 |
| [[entities/compatibility-driven-default-off-performance-features|Compatibility-driven default-off performance features]] | outcome | 1 |
| [[entities/foreground-maintenance-command-blocking|Foreground maintenance command blocking]] | outcome | 3 |
| [[entities/foreground-fetch-overhead|Foreground-fetch overhead]] | outcome | 1 |
| [[entities/index-compression-from-400-mb-to-250-mb|Index compression from 400 MB to 250 MB]] | outcome | 1 |
| [[entities/low-average-index-entry-processing-time|Low average index-entry processing time]] | outcome | 1 |
| [[entities/multi-million-entry-index|Multi-million-entry index]] | outcome | 1 |
| [[entities/performance-decay-from-deferred-cleanup|Performance decay from deferred cleanup]] | outcome | 1 |
| [[entities/system-wide-rewrite-resource-exhaustion|System-wide rewrite resource exhaustion]] | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [[entities/native-git-scalability-improvements|Native Git scalability improvements]] and [[entities/repository-performance-tracing|Repository performance tracing]]: [[synthesis/systems/cur-cont|Cursor Continuity and Origin]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/native-git-scalability-improvements|Native Git scalability improvements]] and [[entities/core-git-capability-consolidation|Core Git capability consolidation]]: [[synthesis/systems/cur-cont|Cursor Continuity and Origin]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/repository-performance-tracing|Repository performance tracing]] and [[entities/core-git-capability-consolidation|Core Git capability consolidation]]: [[synthesis/systems/cur-cont|Cursor Continuity and Origin]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/integrated-client-optimization-configuration|Integrated client optimization configuration]] and [[entities/native-git-scalability-improvements|Native Git scalability improvements]]: [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/integrated-client-optimization-configuration|Integrated client optimization configuration]] and [[entities/repository-performance-tracing|Repository performance tracing]]: [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- 248 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

76 open codes from 18 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
