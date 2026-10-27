---
type: Design Alternative
title: Durable end-to-end feature platform
description: An end-to-end platform prepares data, serves features in real time, and persists engineered feature data for reuse in training, recovery, and subsequent inference.
id: '43.3'
dimension: /concepts/ml-feature-and-data-serving-storage.md
accepted_by:
- s02_p04
- s02_p05
- s02_p06
- s02_p12
- s02_p13
- s05_p06
- s24_p05
rejected_by: []
passages: 7
includes:
- Data-platform ML pipeline
- Real-time feature store
- Durable feature data store
tags:
- value
- accepted
- ml-feature-and-data-serving-storage
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Durable end-to-end feature platform

An end-to-end platform prepares data, serves features in real time, and persists engineered feature data for reuse in training, recovery, and subsequent inference.

## Evidence

- **s02_p04** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p05** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p06** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p12** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p13** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s05_p06** (accepts) · [Microservices Suck for Machine Learning (and what we did about it)](/sources/s5.md)
- **s24_p05** (accepts) · [Automated monitoring of your machine learning models with Amazon SageMaker Model Monitor and sending predictions to human review workflows using Amazon A2I](/sources/s24.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Data-platform ML pipeline**: Product data is transferred to a shared data platform where dedicated ML and data-engineering pipelines prepare it.
- **Real-time feature store**: Streaming and enriched features are materialized in a low-latency store for model use.
- **Durable feature data store**: Persists engineered features for long-term reuse, training, and recovery.
