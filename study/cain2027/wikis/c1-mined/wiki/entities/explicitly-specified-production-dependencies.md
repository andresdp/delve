---
type: Design Alternative
title: Explicitly specified production dependencies
description: Production packages, images, and runtime resources are declared so execution environments can be provisioned and reproduced.
id: '47.1'
dimension: /concepts/ml-dependency-and-service-structure.md
accepted_by:
- s04_p13
- s24_p03
- s25_p06
rejected_by: []
passages: 3
includes:
- Production dependency and environment specification
tags:
- value
- accepted
- ml-dependency-and-service-structure
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Explicitly specified production dependencies

Production packages, images, and runtime resources are declared so execution environments can be provisioned and reproduced. Development or notebook environments are not necessarily governed by the same dependency policy.

## Evidence

- **s04_p13** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s24_p03** (accepts) · [Automated monitoring of your machine learning models with Amazon SageMaker Model Monitor and sending predictions to human review workflows using Amazon A2I](/sources/s24.md)
- **s25_p06** (accepts) · [MLOps: Model management, deployment, and monitoring with Azure Machine Learning](/sources/s25.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Production dependency and environment specification**: Declares packages, images, and runtime resources required for production execution.
