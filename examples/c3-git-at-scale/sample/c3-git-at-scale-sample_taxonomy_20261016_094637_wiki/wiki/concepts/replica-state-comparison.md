---
title: Replica State Comparison
type: dimension
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
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
---

# Replica State Comparison

Which checksum or state-comparison technique verifies equivalence between replica contents?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/checksum-based-replica-state-comparison|Checksum-based replica state comparison]] | accepted | 1 |
| [[entities/incremental-xor-checksum-maintenance|Incremental XOR checksum maintenance]] | accepted | 1 |
| [[entities/full-checksum-recomputation|Full checksum recomputation]] | mixed | 2 |
| [[entities/checksum-equality-as-logical-content-equivalence|Checksum equality as logical-content equivalence]] | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 1 system** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [[entities/checksum-based-replica-state-comparison|Checksum-based replica state comparison]] and [[entities/incremental-xor-checksum-maintenance|Incremental XOR checksum maintenance]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/checksum-based-replica-state-comparison|Checksum-based replica state comparison]] and [[entities/full-checksum-recomputation|Full checksum recomputation]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/incremental-xor-checksum-maintenance|Incremental XOR checksum maintenance]] and [[entities/full-checksum-recomputation|Full checksum recomputation]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]

## Evidence

9 open codes from 2 passages in 2 sources.

**Core dimension:** yes ★ (2 sources, 1 system; core = ≥ 2 sources or ≥ 2 systems).
