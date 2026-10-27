---
type: Design Decision
title: How to automatically process the data used for model building?
description: How to automatically process the data used for model building?
id: '14'
core: true
values: 4
candidate_values: 4
outcomes: 0
evidence:
  codes: 0
  documents: 0
  sources: 0
relations:
- affects How to persist and provide access to features?
- affects How to ingest data into ML projects or applications?
- affects How to parallelize data processing?
- affects Should MLOps be used and if so when?
tags:
- dimension
- core
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-26T11:54:06-03:00'
---

# How to automatically process the data used for model building?

How to automatically process the data used for model building?

## Values

| Value | Status | Passages |
|---|---|---|
| [Data pipeline](/entities/data-pipeline.md) | accepted | 0 |
| [Data processing component](/entities/data-processing-component.md) | accepted | 0 |
| [ETL pipeline](/entities/etl-pipeline.md) | accepted | 0 |
| [No data processing automation](/entities/no-data-processing-automation.md) | accepted | 0 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [How to persist and provide access to features?](/concepts/how-to-persist-and-provide-access-to-features.md). *how to store resulting features*
- Choices on this dimension affect the outcomes of [How to ingest data into ML projects or applications?](/concepts/how-to-ingest-data-into-ml-projects-or-applications.md). *ingest data for data processing and later model building*
- Choices on this dimension affect the outcomes of [How to parallelize data processing?](/concepts/how-to-parallelize-data-processing.md). *Consider If Not Decided Yet*
- Choices on this dimension affect the outcomes of [Should MLOps be used and if so when?](/concepts/should-mlops-be-used-and-if-so-when.md). *data processing automation decision*

### To this dimension

- Choices on [How to perform model building in an ML project?](/concepts/how-to-perform-model-building-in-an-ml-project.md) affect the outcomes of this dimension. *how to automate data processing tasks used by or part of model building*

## Evidence

0 open codes from 0 passages in 0 sources.

**Core dimension:** yes ★ (0 sources; core = ≥ 0 sources).
