---
type: Design Decision
title: Compaction Maintenance Technique
description: Which repacking and object-cleanup techniques maintain compact repository storage?
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
- /synthesis/systems/cur-cont.md
- /synthesis/systems/ms-scalar.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Compaction Maintenance Technique

Which repacking and object-cleanup techniques maintain compact repository storage?

## Values

| Value | Status | Passages |
|---|---|---|
| [Background incremental maintenance](/entities/background-incremental-maintenance.md) | accepted | 8 |
| [Loose-object cleanup](/entities/loose-object-cleanup.md) | accepted | 1 |
| [Single-pack full repacking](/entities/single-pack-full-repacking.md) | rejected | 1 |
| [Loose-object storage overhead](/entities/loose-object-storage-overhead.md) | outcome | 1 |
| [Pack-count and storage reduction](/entities/pack-count-and-storage-reduction.md) | outcome | 1 |
| [Pack-index scan growth](/entities/pack-index-scan-growth.md) | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **1 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.50.

Values adopted together:

- [Background incremental maintenance](/entities/background-incremental-maintenance.md) and [Loose-object cleanup](/entities/loose-object-cleanup.md): [Microsoft Scalar](/synthesis/systems/ms-scalar.md)

## Evidence

8 open codes from 8 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
