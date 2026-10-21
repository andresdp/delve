---
type: Design Decision
title: Replica State Comparison
description: Which checksum or state-comparison technique verifies equivalence between replica contents?
id: '27'
core: true
values: 4
candidate_values: 3
outcomes: 1
evidence:
  codes: 9
  documents: 2
  sources: 2
relations: []
tags:
- dimension
- core
exclusivity: 0.0
systems:
- /synthesis/systems/gh-spokes.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica State Comparison

Which checksum or state-comparison technique verifies equivalence between replica contents?

## Values

| Value | Status | Passages |
|---|---|---|
| [Checksum-based replica state comparison](/entities/checksum-based-replica-state-comparison.md) | accepted | 1 |
| [Incremental XOR checksum maintenance](/entities/incremental-xor-checksum-maintenance.md) | accepted | 1 |
| [Full checksum recomputation](/entities/full-checksum-recomputation.md) | mixed | 2 |
| [Checksum equality as logical-content equivalence](/entities/checksum-equality-as-logical-content-equivalence.md) | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 1 system** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [Checksum-based replica state comparison](/entities/checksum-based-replica-state-comparison.md) and [Incremental XOR checksum maintenance](/entities/incremental-xor-checksum-maintenance.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Checksum-based replica state comparison](/entities/checksum-based-replica-state-comparison.md) and [Full checksum recomputation](/entities/full-checksum-recomputation.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Incremental XOR checksum maintenance](/entities/incremental-xor-checksum-maintenance.md) and [Full checksum recomputation](/entities/full-checksum-recomputation.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)

## Evidence

9 open codes from 2 passages in 2 sources.

**Core dimension:** yes ★ (2 sources, 1 system; core = ≥ 2 sources or ≥ 2 systems).
