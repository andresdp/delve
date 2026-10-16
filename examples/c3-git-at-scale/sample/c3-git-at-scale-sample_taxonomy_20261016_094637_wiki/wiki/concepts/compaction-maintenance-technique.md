---
title: Compaction Maintenance Technique
type: dimension
id: '12'
core: true
values: 6
candidate_values: 3
outcomes: 3
evidence:
  codes: 8
  documents: 8
  sources: 3
relations: []
tags:
- dimension
- core
exclusivity: 0.5
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Compaction Maintenance Technique

Which repacking and object-cleanup techniques maintain compact repository storage?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/background-incremental-maintenance|Background incremental maintenance]] | accepted | 8 |
| [[entities/loose-object-cleanup|Loose-object cleanup]] | accepted | 1 |
| [[entities/single-pack-full-repacking|Single-pack full repacking]] | rejected | 1 |
| [[entities/loose-object-storage-overhead|Loose-object storage overhead]] | outcome | 1 |
| [[entities/pack-count-and-storage-reduction|Pack-count and storage reduction]] | outcome | 1 |
| [[entities/pack-index-scan-growth|Pack-index scan growth]] | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **1 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.50.

Values adopted together:

- [[entities/background-incremental-maintenance|Background incremental maintenance]] and [[entities/loose-object-cleanup|Loose-object cleanup]]: [[synthesis/systems/ms-scalar|Microsoft Scalar]]

## Evidence

8 open codes from 8 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
