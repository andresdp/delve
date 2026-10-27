---
type: Design Decision
title: Model Learning, Tuning, and Update Strategy
description: How selected models learn, tune, update, and adapt during training and operation.
id: '28'
core: true
values: 11
candidate_values: 8
outcomes: 3
evidence:
  codes: 50
  documents: 32
  sources: 13
relations: []
tags:
- dimension
- core
exclusivity: 0.46
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Model Learning, Tuning, and Update Strategy

How selected models learn, tune, update, and adapt during training and operation.

## Values

| Value | Status | Passages |
|---|---|---|
| [Automated hyperparameter optimization](/entities/automated-hyperparameter-optimization.md) | accepted | 13 |
| [Feature-enhanced linear learner](/entities/feature-enhanced-linear-learner.md) | accepted | 2 |
| [Federated model-update learning](/entities/federated-model-update-learning.md) | accepted | 4 |
| [Incremental online training](/entities/incremental-online-training.md) | accepted | 14 |
| [Linear online learner](/entities/linear-online-learner.md) | accepted | 1 |
| [Manual hyperparameter tuning](/entities/manual-hyperparameter-tuning.md) | accepted | 2 |
| [Model optimization objective selection](/entities/model-optimization-objective-selection.md) | accepted | 1 |
| [Client-side model training](/entities/client-side-model-training.md) | mixed | 3 |
| [Hyperparameter search-space burden](/entities/hyperparameter-search-space-burden.md) | outcome | 1 |
| [Near-real-time learning and inference](/entities/near-real-time-learning-and-inference.md) | outcome | 1 |
| [Near-real-time model adaptation](/entities/near-real-time-model-adaptation.md) | outcome | 4 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **6 of 13 sources** adopt one value (or a declared hybrid): exclusivity 0.46.

Values adopted together:

- [Incremental online training](/entities/incremental-online-training.md) and [Automated hyperparameter optimization](/entities/automated-hyperparameter-optimization.md): [s9](/sources/s9.md), [s19](/sources/s19.md), [s22](/sources/s22.md)
- [Incremental online training](/entities/incremental-online-training.md) and [Federated model-update learning](/entities/federated-model-update-learning.md): [s9](/sources/s9.md), [s12](/sources/s12.md), [s19](/sources/s19.md)
- [Automated hyperparameter optimization](/entities/automated-hyperparameter-optimization.md) and [Federated model-update learning](/entities/federated-model-update-learning.md): [s4](/sources/s4.md), [s9](/sources/s9.md), [s19](/sources/s19.md)
- [Linear online learner](/entities/linear-online-learner.md) and [Feature-enhanced linear learner](/entities/feature-enhanced-linear-learner.md): [s11](/sources/s11.md)
- [Linear online learner](/entities/linear-online-learner.md) and [Incremental online training](/entities/incremental-online-training.md): [s11](/sources/s11.md)
- 7 more pair(s)

## Evidence

50 open codes from 32 passages in 13 sources.

**Core dimension:** yes ★ (13 sources; core = ≥ 9 sources).
