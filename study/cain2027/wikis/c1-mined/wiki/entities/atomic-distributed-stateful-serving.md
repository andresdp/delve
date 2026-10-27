---
type: Design Alternative
title: Atomic distributed stateful serving
description: Scalable serving maintains model, feature, or auxiliary state in memory and Redis, updates shared parameters atomically, and distributes work asynchronously.
id: '25.5'
dimension: /concepts/runtime-state-and-communication-strategy.md
accepted_by:
- s11_p04
- s11_p06
- s11_p07
- s12_p05
- s12_p07
rejected_by: []
passages: 5
includes:
- Stateless horizontally scaled inference
- In-memory serving state
- Redis-backed queue and feature storage
- Atomic serving-state updates
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

# Atomic distributed stateful serving

Scalable serving maintains model, feature, or auxiliary state in memory and Redis, updates shared parameters atomically, and distributes work asynchronously.

## Evidence

- **s11_p04** (accepts) · [Architecting a Scalable Real Time Learning System](/sources/s11.md)
- **s11_p06** (accepts) · [Architecting a Scalable Real Time Learning System](/sources/s11.md)
- **s11_p07** (accepts) · [Architecting a Scalable Real Time Learning System](/sources/s11.md)
- **s12_p05** (accepts) · [System Architectures for Personalization and Recommendation](/sources/s12.md)
- **s12_p07** (accepts) · [System Architectures for Personalization and Recommendation](/sources/s12.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Stateless horizontally scaled inference**: Prediction components avoid durable serving state and scale by adding independent instances.
- **In-memory serving state**: Keeps serving parameters or features in memory for low-latency access.
- **Redis-backed queue and feature storage**: Redis provides queueing and key-value storage for features, models, or parameters in serving architectures.
- **Atomic serving-state updates**: Updates shared serving parameters atomically to preserve consistency during rapid model changes.
- **Asynchronous message-driven communication**: Uses non-blocking messaging and workload management between production components.
