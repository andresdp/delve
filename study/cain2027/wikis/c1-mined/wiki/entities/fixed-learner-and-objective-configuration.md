---
type: Design Alternative
title: Fixed learner-and-objective configuration
description: The solution uses a deliberately specified predictive learner together with a task-specific objective, such as gradient-boosted trees with a binary logistic objective.
id: '27.4'
dimension: /concepts/model-family-and-combination-strategy.md
accepted_by:
- s11_p07
- s24_p01
- s24_p04
- s24_p05
rejected_by: []
passages: 4
includes:
- Gradient-boosted tree learner
- Binary logistic objective
tags:
- value
- accepted
- model-family-and-combination-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Fixed learner-and-objective configuration

The solution uses a deliberately specified predictive learner together with a task-specific objective, such as gradient-boosted trees with a binary logistic objective.

## Evidence

- **s11_p07** (accepts) · [Architecting a Scalable Real Time Learning System](/sources/s11.md)
- **s24_p01** (accepts) · [Automated monitoring of your machine learning models with Amazon SageMaker Model Monitor and sending predictions to human review workflows using Amazon A2I](/sources/s24.md)
- **s24_p04** (accepts) · [Automated monitoring of your machine learning models with Amazon SageMaker Model Monitor and sending predictions to human review workflows using Amazon A2I](/sources/s24.md)
- **s24_p05** (accepts) · [Automated monitoring of your machine learning models with Amazon SageMaker Model Monitor and sending predictions to human review workflows using Amazon A2I](/sources/s24.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Gradient-boosted tree learner**: Using gradient-boosted decision trees as the predictive model family.
- **Binary logistic objective**: Configuring a learner with a Bernoulli/logistic objective for binary classification.
