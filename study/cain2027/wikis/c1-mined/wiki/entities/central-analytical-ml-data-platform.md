---
type: Design Alternative
title: Central analytical ML data platform
description: Prepared product data is transferred to a shared analytical data platform, where ML and data-engineering pipelines expose data for downstream use.
id: '43.1'
dimension: /concepts/ml-feature-and-data-serving-storage.md
accepted_by:
- s01_p05
- s01_p06
- s09_p08
- s15_p05
- s18_p01
- s29_p02
rejected_by: []
passages: 6
includes:
- Data-platform ML pipeline
- Analytical datastore selection
tags:
- value
- accepted
- ml-feature-and-data-serving-storage
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Central analytical ML data platform

Prepared product data is transferred to a shared analytical data platform, where ML and data-engineering pipelines expose data for downstream use. The platform may combine analytical storage with ML-oriented preparation.

## Evidence

- **s01_p05** (accepts) · [How to power up your product by machine learning with python microservice, pt. 1](/sources/s1.md)
- **s01_p06** (accepts) · [How to power up your product by machine learning with python microservice, pt. 1](/sources/s1.md)
- **s09_p08** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)
- **s15_p05** (accepts) · [Scalable Software and Big Data Architecture - Big Data and Analytics Architectural Patterns](/sources/s15.md)
- **s18_p01** (accepts) · [AutoML is Overhyped](/sources/s18.md)
- **s29_p02** (accepts) · [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Data-platform ML pipeline**: Product data is transferred to a shared data platform where dedicated ML and data-engineering pipelines prepare it.
- **Analytical datastore selection**: Selects the warehouse, lake, OLAP system, or analytics database used to expose analytical data.
