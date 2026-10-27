---
type: Design Decision
title: Model Family and Combination Strategy
description: Which predictive model families or combinations are selected for the ML solution.
id: '27'
core: true
values: 5
candidate_values: 5
outcomes: 0
evidence:
  codes: 29
  documents: 26
  sources: 13
relations:
- affects Model Evaluation and Regression Strategy
- affects Runtime State and Communication Strategy
tags:
- dimension
- core
exclusivity: 1.0
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Model Family and Combination Strategy

Which predictive model families or combinations are selected for the ML solution.

## Values

| Value | Status | Passages |
|---|---|---|
| [Automated model-family selection](/entities/automated-model-family-selection.md) | accepted | 8 |
| [Ensemble-oriented automated modeling](/entities/ensemble-oriented-automated-modeling.md) | accepted | 3 |
| [Fixed learner-and-objective configuration](/entities/fixed-learner-and-objective-configuration.md) | accepted | 4 |
| [Service-based configurable model building](/entities/service-based-configurable-model-building.md) | accepted | 10 |
| [Nonlinear online learner](/entities/nonlinear-online-learner.md) | rejected | 1 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Model Evaluation and Regression Strategy](/concepts/model-evaluation-and-regression-strategy.md). *Different learner families require different evaluation criteria, tests, and acceptable performance trade-offs.*
- Choices on this dimension affect the outcomes of [Runtime State and Communication Strategy](/concepts/runtime-state-and-communication-strategy.md). *Model complexity and prediction representation influence serving memory, latency, and hardware requirements.*

### To this dimension

- Choices on [Training Execution and Scaling Strategy](/concepts/training-execution-and-scaling-strategy.md) affect the outcomes of this dimension. *Incremental, parallel, or distributed execution changes which algorithms, update methods, and model candidates are practical.*
- Choices on [Production Monitoring and Adaptation](/concepts/production-monitoring-and-adaptation.md) affect the outcomes of this dimension. *Observed decay, bias, or changing input distributions can prompt a different learner or a new model version.*

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **13 of 13 sources** adopt one value (or a declared hybrid): exclusivity 1.00.

## Evidence

29 open codes from 26 passages in 13 sources.

**Core dimension:** yes ★ (13 sources; core = ≥ 9 sources).
