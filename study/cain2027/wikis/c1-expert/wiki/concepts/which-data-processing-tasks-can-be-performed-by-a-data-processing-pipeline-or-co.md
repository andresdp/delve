---
type: Design Decision
title: Which data processing tasks can be performed by a data processing pipeline or component?
description: Which data processing tasks can be performed by a data processing pipeline or component?
id: '16'
core: true
values: 7
candidate_values: 7
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

# Which data processing tasks can be performed by a data processing pipeline or component?

Which data processing tasks can be performed by a data processing pipeline or component?

## Values

| Value | Status | Passages |
|---|---|---|
| [Data extraction](/entities/data-extraction.md) | accepted | 0 |
| [Data preparation](/entities/data-preparation.md) | accepted | 0 |
| [Data processing hyperparameter tuning](/entities/data-processing-hyperparameter-tuning.md) | accepted | 0 |
| [Data selection](/entities/data-selection.md) | accepted | 0 |
| [Data transformation](/entities/data-transformation.md) | accepted | 0 |
| [Data validation](/entities/data-validation.md) | accepted | 0 |
| [Feature engineering](/entities/feature-engineering.md) | accepted | 0 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Should AutoML be used and if so where?](/concepts/should-automl-be-used-and-if-so-where.md). *should data processing tasks be automated based on AutoML?*
- Choices on this dimension affect the outcomes of [Should MLOps be used and if so when?](/concepts/should-mlops-be-used-and-if-so-when.md). *data processing tasks decision*


## Evidence

0 open codes from 0 passages in 0 sources.

**Core dimension:** yes ★ (0 sources; core = ≥ 0 sources).
