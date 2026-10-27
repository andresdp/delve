---
type: Design Decision
title: Which tasks can be performed by a model building pipeline or component?
description: Which tasks can be performed by a model building pipeline or component?
id: '20'
core: true
values: 10
candidate_values: 10
outcomes: 0
evidence:
  codes: 0
  documents: 0
  sources: 0
relations:
- affects Should AutoML be used and if so where?
- affects Should MLOps be used and if so when?
tags:
- dimension
- core
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-26T11:54:06-03:00'
---

# Which tasks can be performed by a model building pipeline or component?

Which tasks can be performed by a model building pipeline or component?

## Values

| Value | Status | Passages |
|---|---|---|
| [Data checkpoints](/entities/data-checkpoints.md) | accepted | 0 |
| [Data splitting](/entities/data-splitting.md) | accepted | 0 |
| [Development tool export](/entities/development-tool-export.md) | accepted | 0 |
| [Development tool facade](/entities/development-tool-facade.md) | accepted | 0 |
| [Model hyperparameter tuning](/entities/model-hyperparameter-tuning.md) | accepted | 0 |
| [Model packaging](/entities/model-packaging.md) | accepted | 0 |
| [Model selection](/entities/model-selection.md) | accepted | 0 |
| [Model training](/entities/model-training.md) | accepted | 0 |
| [Model validation](/entities/model-validation.md) | accepted | 0 |
| [Train multiple model versions with different parameters and/or algorithms](/entities/train-multiple-model-versions-with-different-parameters-and-or-algorithms.md) | accepted | 0 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Should AutoML be used and if so where?](/concepts/should-automl-be-used-and-if-so-where.md). *should model building tasks be automated based on AutoML?*
- Choices on this dimension affect the outcomes of [Should MLOps be used and if so when?](/concepts/should-mlops-be-used-and-if-so-when.md). *model building tasks decision*


## Evidence

0 open codes from 0 passages in 0 sources.

**Core dimension:** yes ★ (0 sources; core = ≥ 0 sources).
