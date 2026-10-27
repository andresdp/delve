---
type: Design Alternative
title: Stateless horizontally scaled serving
description: Serving instances avoid durable serving state and handle requests independently, scaling out by adding replicas.
id: '25.1'
dimension: /concepts/runtime-state-and-communication-strategy.md
accepted_by:
- s01_p02
- s04_p01
rejected_by: []
passages: 2
includes:
- Stateless horizontally scaled inference
tags:
- value
- accepted
- runtime-state-and-communication-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Stateless horizontally scaled serving

Serving instances avoid durable serving state and handle requests independently, scaling out by adding replicas.

## Evidence

- **s01_p02** (accepts) · [How to power up your product by machine learning with python microservice, pt. 1](/sources/s1.md)
- **s04_p01** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Stateless horizontally scaled inference**: Prediction components avoid durable serving state and scale by adding independent instances.
