---
type: Design Alternative
title: Online feature-serving pipeline
description: A shared preparation pipeline produces and materializes features in a low-latency serving store for online model inference.
id: '43.2'
dimension: /concepts/ml-feature-and-data-serving-storage.md
accepted_by:
- s04_p01
- s04_p04
- s04_p05
- s04_p11
- s13_p11
- s20_p06
- s22_p03
- s22_p17
rejected_by: []
passages: 8
includes:
- Data-platform ML pipeline
- Real-time feature store
tags:
- value
- accepted
- ml-feature-and-data-serving-storage
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Online feature-serving pipeline

A shared preparation pipeline produces and materializes features in a low-latency serving store for online model inference.

## Evidence

- **s04_p01** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p04** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p05** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p11** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s13_p11** (accepts) · [Architectural thinking in the Wild West of data science](/sources/s13.md)
- **s20_p06** (accepts) · [MLOps: Methods and Tools of DevOps for Machine Learning](/sources/s20.md)
- **s22_p03** (accepts) · [MLOps Principles](/sources/s22.md)
- **s22_p17** (accepts) · [MLOps Principles](/sources/s22.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Data-platform ML pipeline**: Product data is transferred to a shared data platform where dedicated ML and data-engineering pipelines prepare it.
- **Real-time feature store**: Streaming and enriched features are materialized in a low-latency store for model use.
