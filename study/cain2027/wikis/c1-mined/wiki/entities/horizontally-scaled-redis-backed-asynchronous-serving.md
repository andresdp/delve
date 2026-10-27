---
type: Design Alternative
title: Horizontally scaled Redis-backed asynchronous serving
description: Stateless or independently scalable serving instances use Redis for feature or queue storage while exchanging work asynchronously.
id: '25.3'
dimension: /concepts/runtime-state-and-communication-strategy.md
accepted_by:
- s02_p01
- s02_p05
- s02_p11
- s02_p13
- s19_p15
rejected_by: []
passages: 5
includes:
- Stateless horizontally scaled inference
- Redis-backed queue and feature storage
- Asynchronous message-driven communication
tags:
- value
- accepted
- runtime-state-and-communication-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Horizontally scaled Redis-backed asynchronous serving

Stateless or independently scalable serving instances use Redis for feature or queue storage while exchanging work asynchronously.

## Evidence

- **s02_p01** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p05** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p11** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s02_p13** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s19_p15** (accepts) · [Three Levels of ML Software](/sources/s19.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Stateless horizontally scaled inference**: Prediction components avoid durable serving state and scale by adding independent instances.
- **Redis-backed queue and feature storage**: Redis provides queueing and key-value storage for features, models, or parameters in serving architectures.
- **Asynchronous message-driven communication**: Uses non-blocking messaging and workload management between production components.
