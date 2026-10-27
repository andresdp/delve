---
type: Design Alternative
title: Pipeline and experiment version control
description: Pipeline definitions, ML artifacts, and experiments are versioned together so alternative configurations and training results can be compared and reproduced.
id: '20.2'
dimension: /concepts/ml-artifact-and-lifecycle-versioning.md
accepted_by:
- s04_p01
- s04_p03
- s04_p05
- s04_p15
- s04_p18
- s17_p03
rejected_by: []
passages: 6
includes:
- Pipeline design versioning
- ML artifact versioning and dependency management
- Experiment tracking and model benchmarking
tags:
- value
- accepted
- ml-artifact-and-lifecycle-versioning
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Pipeline and experiment version control

Pipeline definitions, ML artifacts, and experiments are versioned together so alternative configurations and training results can be compared and reproduced.

## Evidence

- **s04_p01** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p03** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p05** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p15** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p18** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s17_p03** (accepts) · [AutoML](/sources/s17.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Pipeline design versioning**: Pipeline designs are cloned or otherwise versioned so iterations can preserve earlier configurations.
- **ML artifact versioning and dependency management**: Versions models, code, data, parameters, tests, and dependencies as deployable ML assets.
- **Experiment tracking and model benchmarking**: Systematic collection and comparison of training runs, hyperparameters, metrics, and resulting models.
