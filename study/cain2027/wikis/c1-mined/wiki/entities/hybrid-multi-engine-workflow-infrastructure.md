---
type: Design Alternative
title: Hybrid multi-engine workflow infrastructure
description: Combines managed ML services and pipeline capabilities with pluggable execution engines so workflows can run across selectable or specialized runtimes.
id: '33.3'
dimension: /concepts/ml-workflow-infrastructure-strategy.md
accepted_by:
- s04_p05
- s04_p07
- s04_p14
- s04_p17
- s06_p07
- s06_p13
- s06_p15
- s08_p02
- s09_p07
- s09_p08
rejected_by: []
passages: 10
includes:
- Managed cloud ML platform
- Managed ML pipeline platform
- Pluggable execution engine
tags:
- value
- accepted
- ml-workflow-infrastructure-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Hybrid multi-engine workflow infrastructure

Combines managed ML services and pipeline capabilities with pluggable execution engines so workflows can run across selectable or specialized runtimes.

## Evidence

- **s04_p05** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p07** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p14** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p17** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s06_p07** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p13** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p15** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s08_p02** (accepts) · [Continuous Intelligence: Moving Machine Learning Application into Production Reliably](/sources/s8.md)
- **s09_p07** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)
- **s09_p08** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Managed cloud ML platform**: Uses a managed cloud service for model creation, training, and deployment infrastructure.
- **Managed ML pipeline platform**: Uses managed pipeline components and templates to build and operate ML workflows.
- **Pluggable execution engine**: Runs registered functions through selectable Kubernetes, Spark, or other runtime engines.
