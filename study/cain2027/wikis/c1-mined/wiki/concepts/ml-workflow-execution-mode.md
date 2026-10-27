---
type: Design Decision
title: ML Workflow Execution Mode
description: How training, inference, offline execution, and execution instrumentation are separated or combined.
id: '34'
core: false
values: 3
candidate_values: 3
outcomes: 0
evidence:
  codes: 8
  documents: 9
  sources: 5
relations: []
tags:
- dimension
exclusivity: 0.4
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Workflow Execution Mode

How training, inference, offline execution, and execution instrumentation are separated or combined.

## Values

| Value | Status | Passages |
|---|---|---|
| [Instrumented execution wrapper](/entities/instrumented-execution-wrapper.md) | accepted | 1 |
| [Offline training pipeline](/entities/offline-training-pipeline.md) | accepted | 6 |
| [Separated training and inference workflow](/entities/separated-training-and-inference-workflow.md) | accepted | 5 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **2 of 5 sources** adopt one value (or a declared hybrid): exclusivity 0.40.

Values adopted together:

- [Separated training and inference workflow](/entities/separated-training-and-inference-workflow.md) and [Offline training pipeline](/entities/offline-training-pipeline.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s19](/sources/s19.md)

## Evidence

8 open codes from 9 passages in 5 sources.

**Core dimension:** no (5 sources; core = ≥ 9 sources).
