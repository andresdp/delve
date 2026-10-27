---
type: Design Decision
title: How to serve model predictions or scores?
description: How to serve model predictions or scores?
id: '5'
core: true
values: 5
candidate_values: 5
outcomes: 0
evidence:
  codes: 0
  documents: 0
  sources: 0
relations:
- affects How to persist and provide access to features?
- affects How to inform clients about prediction result availability?
- affects How to ingest data into ML projects or applications?
tags:
- dimension
- core
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-26T11:54:06-03:00'
---

# How to serve model predictions or scores?

How to serve model predictions or scores?

## Values

| Value | Status | Passages |
|---|---|---|
| [Data batch based model serving](/entities/data-batch-based-model-serving.md) | accepted | 0 |
| [Hybrid online/offline model serving](/entities/hybrid-online-offline-model-serving.md) | accepted | 0 |
| [Local service/API based model serving](/entities/local-service-api-based-model-serving.md) | accepted | 0 |
| [Microservice based model serving](/entities/microservice-based-model-serving.md) | accepted | 0 |
| [Precompute serving](/entities/precompute-serving.md) | accepted | 0 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [How to persist and provide access to features?](/concepts/how-to-persist-and-provide-access-to-features.md). *how to access features for model serving*
- Choices on this dimension affect the outcomes of [How to inform clients about prediction result availability?](/concepts/how-to-inform-clients-about-prediction-result-availability.md). *Consider If Not Decided Yet*
- Choices on this dimension affect the outcomes of [How to ingest data into ML projects or applications?](/concepts/how-to-ingest-data-into-ml-projects-or-applications.md). *ingest data required during model serving*

### To this dimension

- Choices on [How to integrate a machine learning model in an application?](/concepts/how-to-integrate-a-machine-learning-model-in-an-application.md) affect the outcomes of this dimension. *Consider If Not Decided Yet*

## Evidence

0 open codes from 0 passages in 0 sources.

**Core dimension:** yes ★ (0 sources; core = ≥ 0 sources).
