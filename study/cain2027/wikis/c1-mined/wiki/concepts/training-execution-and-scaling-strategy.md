---
type: Design Decision
title: Training Execution and Scaling Strategy
description: Varies how training workloads execute, scale, and allocate compute, independently of which predictive algorithm is selected.
id: '3'
core: true
values: 6
candidate_values: 5
outcomes: 1
evidence:
  codes: 16
  documents: 20
  sources: 10
relations:
- affects Model Family and Combination Strategy
- constrains Runtime State and Communication Strategy
tags:
- dimension
- core
exclusivity: 0.44
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Training Execution and Scaling Strategy

Varies how training workloads execute, scale, and allocate compute, independently of which predictive algorithm is selected.

## Values

| Value | Status | Passages |
|---|---|---|
| [Distributed event computation](/entities/distributed-event-computation.md) | accepted | 7 |
| [Fault-tolerant partitioned training](/entities/fault-tolerant-partitioned-training.md) | accepted | 2 |
| [Horizontal and vertical training scalability](/entities/horizontal-and-vertical-training-scalability.md) | accepted | 4 |
| [Parallel candidate training](/entities/parallel-candidate-training.md) | accepted | 8 |
| [Vertically scalable training](/entities/vertically-scalable-training.md) | accepted | 2 |
| [Distributed-training scalability requirement](/entities/distributed-training-scalability-requirement.md) | outcome | 4 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Model Family and Combination Strategy](/concepts/model-family-and-combination-strategy.md). *Incremental, parallel, or distributed execution changes which algorithms, update methods, and model candidates are practical.*
- Choices on this dimension limit the options available on [Runtime State and Communication Strategy](/concepts/runtime-state-and-communication-strategy.md). *Training scale and memory behavior determine suitable hardware, state handling, and resource allocation.*

### To this dimension

- Choices on [Data Ingestion Mechanism](/concepts/data-ingestion-mechanism.md) affect the outcomes of this dimension. *Ingestion mode, feature transformations, and available datasets determine training inputs, freshness, and execution requirements.*

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **4 of 9 sources** adopt one value (or a declared hybrid): exclusivity 0.44.

Values adopted together:

- [Horizontal and vertical training scalability](/entities/horizontal-and-vertical-training-scalability.md) and [Distributed event computation](/entities/distributed-event-computation.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s15](/sources/s15.md)
- [Distributed event computation](/entities/distributed-event-computation.md) and [Parallel candidate training](/entities/parallel-candidate-training.md): [s2](/sources/s2.md), [s4](/sources/s4.md)
- [Fault-tolerant partitioned training](/entities/fault-tolerant-partitioned-training.md) and [Parallel candidate training](/entities/parallel-candidate-training.md): [s2](/sources/s2.md), [s22](/sources/s22.md)
- [Vertically scalable training](/entities/vertically-scalable-training.md) and [Horizontal and vertical training scalability](/entities/horizontal-and-vertical-training-scalability.md): [s12](/sources/s12.md)
- [Vertically scalable training](/entities/vertically-scalable-training.md) and [Distributed event computation](/entities/distributed-event-computation.md): [s12](/sources/s12.md)
- 3 more pair(s)

## Evidence

16 open codes from 20 passages in 10 sources.

**Core dimension:** yes ★ (10 sources; core = ≥ 9 sources).
