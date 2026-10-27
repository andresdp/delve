---
type: Design Alternative
title: Asynchronous message-driven serving
description: Production components communicate through non-blocking messages and queues, decoupling request handling from downstream work.
id: '25.2'
dimension: /concepts/runtime-state-and-communication-strategy.md
accepted_by:
- s07_p01
- s10_p04
- s16_p04
- s16_p05
rejected_by: []
passages: 4
includes:
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

# Asynchronous message-driven serving

Production components communicate through non-blocking messages and queues, decoupling request handling from downstream work.

## Evidence

- **s07_p01** (accepts) · [Composing Deep-Learning Microservices for the Hybrid Internet of Things](/sources/s7.md)
- **s10_p04** (accepts) · [Architecting a Machine Learning System for Risk](/sources/s10.md)
- **s16_p04** (accepts) · [Machine Learning in Production: Software Architecture](/sources/s16.md)
- **s16_p05** (accepts) · [Machine Learning in Production: Software Architecture](/sources/s16.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Asynchronous message-driven communication**: Uses non-blocking messaging and workload management between production components.
