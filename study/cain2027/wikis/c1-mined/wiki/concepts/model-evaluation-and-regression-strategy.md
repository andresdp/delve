---
type: Design Decision
title: Model Evaluation and Regression Strategy
description: Varies how model quality and regressions are assessed before promotion.
id: '13'
core: true
values: 15
candidate_values: 14
outcomes: 1
evidence:
  codes: 41
  documents: 32
  sources: 13
relations:
- affects Production Monitoring and Adaptation
- requires ML Workflow Execution Coordination
tags:
- dimension
- core
exclusivity: 0.31
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Model Evaluation and Regression Strategy

Varies how model quality and regressions are assessed before promotion.

## Values

| Value | Status | Passages |
|---|---|---|
| [Business-impact-aligned evaluation](/entities/business-impact-aligned-evaluation.md) | accepted | 4 |
| [Fairness and inclusion evaluation](/entities/fairness-and-inclusion-evaluation.md) | accepted | 4 |
| [Feature infrastructure cost evaluation](/entities/feature-infrastructure-cost-evaluation.md) | accepted | 1 |
| [Feature predictive-power evaluation](/entities/feature-predictive-power-evaluation.md) | accepted | 1 |
| [Held-out test-set isolation](/entities/held-out-test-set-isolation.md) | accepted | 6 |
| [Interpretability-oriented model evaluation](/entities/interpretability-oriented-model-evaluation.md) | accepted | 5 |
| [Metric-driven candidate model evaluation](/entities/metric-driven-candidate-model-evaluation.md) | accepted | 10 |
| [Model staleness testing](/entities/model-staleness-testing.md) | accepted | 3 |
| [Offline evaluation pipeline](/entities/offline-evaluation-pipeline.md) | accepted | 9 |
| [Risk-specific model evaluation](/entities/risk-specific-model-evaluation.md) | accepted | 3 |
| [Separated training and test-data collection](/entities/separated-training-and-test-data-collection.md) | accepted | 5 |
| [Threshold-based quality regression testing](/entities/threshold-based-quality-regression-testing.md) | accepted | 6 |
| [Previously-built-model diff testing](/entities/previously-built-model-diff-testing.md) | mixed | 4 |
| [Single-objective evaluation](/entities/single-objective-evaluation.md) | rejected | 1 |
| [Ground-truth quality assessment](/entities/ground-truth-quality-assessment.md) | outcome | 2 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Production Monitoring and Adaptation](/concepts/production-monitoring-and-adaptation.md). *Pre-production thresholds and validation criteria establish the quality signals later monitored for regression and decay.*
- This dimension requires [ML Workflow Execution Coordination](/concepts/ml-workflow-execution-coordination.md) to be decided first. *Automated integration, regression, and canary checks depend on the workflow and release path being established.*

### To this dimension

- Choices on [Model Family and Combination Strategy](/concepts/model-family-and-combination-strategy.md) affect the outcomes of this dimension. *Different learner families require different evaluation criteria, tests, and acceptable performance trade-offs.*
- Choices on [Runtime State and Communication Strategy](/concepts/runtime-state-and-communication-strategy.md) affect the outcomes of this dimension. *Runtime resource and state choices influence latency, throughput, compatibility, and the feasibility of production tests.*

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **4 of 13 sources** adopt one value (or a declared hybrid): exclusivity 0.31.

Values adopted together:

- [Offline evaluation pipeline](/entities/offline-evaluation-pipeline.md) and [Metric-driven candidate model evaluation](/entities/metric-driven-candidate-model-evaluation.md): [s2](/sources/s2.md), [s9](/sources/s9.md), [s22](/sources/s22.md), [s25](/sources/s25.md)
- [Offline evaluation pipeline](/entities/offline-evaluation-pipeline.md) and [Threshold-based quality regression testing](/entities/threshold-based-quality-regression-testing.md): [s6](/sources/s6.md), [s9](/sources/s9.md), [s22](/sources/s22.md)
- [Offline evaluation pipeline](/entities/offline-evaluation-pipeline.md) and [Separated training and test-data collection](/entities/separated-training-and-test-data-collection.md): [s8](/sources/s8.md), [s9](/sources/s9.md), [s22](/sources/s22.md)
- [Held-out test-set isolation](/entities/held-out-test-set-isolation.md) and [Metric-driven candidate model evaluation](/entities/metric-driven-candidate-model-evaluation.md): [s9](/sources/s9.md), [s19](/sources/s19.md), [s22](/sources/s22.md)
- [Held-out test-set isolation](/entities/held-out-test-set-isolation.md) and [Separated training and test-data collection](/entities/separated-training-and-test-data-collection.md): [s9](/sources/s9.md), [s19](/sources/s19.md), [s22](/sources/s22.md)
- 70 more pair(s)

## Evidence

41 open codes from 32 passages in 13 sources.

**Core dimension:** yes ★ (13 sources; core = ≥ 9 sources).
