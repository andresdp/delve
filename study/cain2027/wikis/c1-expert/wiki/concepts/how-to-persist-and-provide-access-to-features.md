---
type: Design Decision
title: How to persist and provide access to features?
description: How to persist and provide access to features?
id: '4'
core: true
values: 2
candidate_values: 2
outcomes: 0
evidence:
  codes: 0
  documents: 0
  sources: 0
relations:
- affects Should MLOps be used and if so when?
tags:
- dimension
- core
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-26T11:54:06-03:00'
---

# How to persist and provide access to features?

How to persist and provide access to features?

## Values

| Value | Status | Passages |
|---|---|---|
| [Feature store](/entities/feature-store.md) | accepted | 0 |
| [Store features in data stores without specific support](/entities/store-features-in-data-stores-without-specific-support.md) | accepted | 0 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Should MLOps be used and if so when?](/concepts/should-mlops-be-used-and-if-so-when.md). *feature persistence and access decision*

### To this dimension

- Choices on [How to serve model predictions or scores?](/concepts/how-to-serve-model-predictions-or-scores.md) affect the outcomes of this dimension. *how to access features for model serving*
- Choices on [How to automatically process the data used for model building?](/concepts/how-to-automatically-process-the-data-used-for-model-building.md) affect the outcomes of this dimension. *how to store resulting features*
- Choices on [How to perform model building in an ML project?](/concepts/how-to-perform-model-building-in-an-ml-project.md) affect the outcomes of this dimension. *how to access features for model training*

## Evidence

0 open codes from 0 passages in 0 sources.

**Core dimension:** yes ★ (0 sources; core = ≥ 0 sources).
