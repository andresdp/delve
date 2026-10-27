---
type: Design Alternative
title: Online/offline feature-store architecture
description: Features are maintained in complementary online and durable stores, separating low-latency inference access from persistent training and reuse needs.
id: '43.4'
dimension: /concepts/ml-feature-and-data-serving-storage.md
accepted_by:
- s06_p09
- s21_p09
rejected_by: []
passages: 2
includes:
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

# Online/offline feature-store architecture

Features are maintained in complementary online and durable stores, separating low-latency inference access from persistent training and reuse needs.

## Evidence

- **s06_p09** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s21_p09** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Real-time feature store**: Streaming and enriched features are materialized in a low-latency store for model use.
- **Durable feature data store**: Persists engineered features for long-term reuse, training, and recovery.
