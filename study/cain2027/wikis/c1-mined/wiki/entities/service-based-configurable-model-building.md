---
type: Design Alternative
title: Service-based configurable model building
description: A reusable model-building service trains and selects models through configurable algorithms, parameters, and metrics.
id: '27.2'
dimension: /concepts/model-family-and-combination-strategy.md
accepted_by:
- s02_p04
- s02_p08
- s02_p09
- s09_p07
- s09_p09
- s10_p03
- s10_p05
- s10_p09
- s22_p08
- s22_p17
rejected_by: []
passages: 10
includes:
- Random forest learner
- Automated model-family selection
- Dedicated model-builder service
- Interchangeable model-algorithm library
tags:
- value
- accepted
- model-family-and-combination-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Service-based configurable model building

A reusable model-building service trains and selects models through configurable algorithms, parameters, and metrics. It can support interchangeable learner implementations and specified families such as random forests.

## Evidence

- **s02_p04** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p08** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p09** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s09_p07** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)
- **s09_p09** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)
- **s10_p03** (accepts) · [Architecting a Machine Learning System for Risk](/sources/s10.md)
- **s10_p05** (accepts) · [Architecting a Machine Learning System for Risk](/sources/s10.md)
- **s10_p09** (accepts) · [Architecting a Machine Learning System for Risk](/sources/s10.md)
- **s22_p08** (accepts) · [MLOps Principles](/sources/s22.md)
- **s22_p17** (accepts) · [MLOps Principles](/sources/s22.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Random forest learner**: Random forests are selected when their precision-recall balance fits the intended application.
- **Automated model-family selection**: Selects among alternative learner families according to predictive score, time, or workflow objectives.
- **Dedicated model-builder service**: Separates candidate training and metric-driven model selection into a reusable model-building service.
- **Interchangeable model-algorithm library**: Uses a replaceable library of algorithms so model types can be added and exchanged in training pipelines.
