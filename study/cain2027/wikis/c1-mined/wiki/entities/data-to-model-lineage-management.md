---
type: Design Alternative
title: Data-to-model lineage management
description: Dataset versions and profiles are linked to reproducible training context, model metadata, registry information, and deployment status.
id: '20.4'
dimension: /concepts/ml-artifact-and-lifecycle-versioning.md
accepted_by:
- s10_p08
- s20_p03
- s20_p05
- s20_p08
rejected_by: []
passages: 4
includes:
- ML artifact versioning and dependency management
- Training run snapshotting
- Metadata-based ML lifecycle audit trail
- Model registry and deployment-health tracking
- Dataset profiling and versioning
tags:
- value
- accepted
- ml-artifact-and-lifecycle-versioning
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Data-to-model lineage management

Dataset versions and profiles are linked to reproducible training context, model metadata, registry information, and deployment status.

## Evidence

- **s10_p08** (accepts) · [Architecting a Machine Learning System for Risk](/sources/s10.md)
- **s20_p03** (accepts) · [MLOps: Methods and Tools of DevOps for Machine Learning](/sources/s20.md)
- **s20_p05** (accepts) · [MLOps: Methods and Tools of DevOps for Machine Learning](/sources/s20.md)
- **s20_p08** (accepts) · [MLOps: Methods and Tools of DevOps for Machine Learning](/sources/s20.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **ML artifact versioning and dependency management**: Versions models, code, data, parameters, tests, and dependencies as deployable ML assets.
- **Training run snapshotting**: Capturing code, data, model, parameters, and compute context for reproducible training runs.
- **Metadata-based ML lifecycle audit trail**: Using metadata across data, code, models, and pipeline stages to audit and reproduce the ML lifecycle.
- **Model registry and deployment-health tracking**: Maintaining registered model metadata together with deployment and operational health information.
- **Dataset profiling and versioning**: Profiling datasets and maintaining versions of the data used by ML workflows.
