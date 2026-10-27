---
type: Design Alternative
title: Pipeline-based CI/CD governance
description: Pipeline designs, experiments, lifecycle metadata, registered models, and deployment health are managed through an operational CI/CD governance process.
id: '20.5'
dimension: /concepts/ml-artifact-and-lifecycle-versioning.md
accepted_by:
- s06_p02
- s06_p07
- s06_p13
- s09_p10
- s09_p11
rejected_by: []
passages: 5
includes:
- Pipeline design versioning
- Experiment tracking and model benchmarking
- Metadata-based ML lifecycle audit trail
- Model registry and deployment-health tracking
tags:
- value
- accepted
- ml-artifact-and-lifecycle-versioning
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Pipeline-based CI/CD governance

Pipeline designs, experiments, lifecycle metadata, registered models, and deployment health are managed through an operational CI/CD governance process.

## Evidence

- **s06_p02** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p07** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p13** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s09_p10** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)
- **s09_p11** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Pipeline design versioning**: Pipeline designs are cloned or otherwise versioned so iterations can preserve earlier configurations.
- **Experiment tracking and model benchmarking**: Systematic collection and comparison of training runs, hyperparameters, metrics, and resulting models.
- **Metadata-based ML lifecycle audit trail**: Using metadata across data, code, models, and pipeline stages to audit and reproduce the ML lifecycle.
- **Model registry and deployment-health tracking**: Maintaining registered model metadata together with deployment and operational health information.
