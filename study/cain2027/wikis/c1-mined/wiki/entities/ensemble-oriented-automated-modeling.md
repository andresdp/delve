---
type: Design Alternative
title: Ensemble-oriented automated modeling
description: The solution combines multiple models, potentially using an automated or packaged AutoML process to select and blend them for improved predictive performance or stability.
id: '27.3'
dimension: /concepts/model-family-and-combination-strategy.md
accepted_by:
- s12_p07
- s18_p01
- s18_p02
rejected_by: []
passages: 3
includes:
- Automated model-family selection
- Model ensembling
- Boxed AutoML tool
tags:
- value
- accepted
- model-family-and-combination-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Ensemble-oriented automated modeling

The solution combines multiple models, potentially using an automated or packaged AutoML process to select and blend them for improved predictive performance or stability.

## Evidence

- **s12_p07** (accepts) · [System Architectures for Personalization and Recommendation](/sources/s12.md)
- **s18_p01** (accepts) · [AutoML is Overhyped](/sources/s18.md)
- **s18_p02** (accepts) · [AutoML is Overhyped](/sources/s18.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Automated model-family selection**: Selects among alternative learner families according to predictive score, time, or workflow objectives.
- **Model ensembling**: Combines multiple trained models to improve stability or predictive score.
- **Boxed AutoML tool**: Packaged off-the-shelf AutoML is rejected as the chosen modeling approach.
