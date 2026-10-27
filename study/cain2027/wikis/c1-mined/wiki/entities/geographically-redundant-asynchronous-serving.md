---
type: Design Alternative
title: Geographically redundant asynchronous serving
description: Serving is distributed across regions or continents, using asynchronous operation and failover to maintain availability under regional failures.
id: '25.4'
dimension: /concepts/runtime-state-and-communication-strategy.md
accepted_by:
- s13_p09
- s13_p10
- s15_p03
- s15_p04
rejected_by: []
passages: 4
includes:
- Stateless horizontally scaled inference
- Asynchronous message-driven communication
- Geographic high availability and failover
tags:
- value
- accepted
- runtime-state-and-communication-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Geographically redundant asynchronous serving

Serving is distributed across regions or continents, using asynchronous operation and failover to maintain availability under regional failures.

## Evidence

- **s13_p09** (accepts) · [Architectural thinking in the Wild West of data science](/sources/s13.md)
- **s13_p10** (accepts) · [Architectural thinking in the Wild West of data science](/sources/s13.md)
- **s15_p03** (accepts) · [Scalable Software and Big Data Architecture - Big Data and Analytics Architectural Patterns](/sources/s15.md)
- **s15_p04** (accepts) · [Scalable Software and Big Data Architecture - Big Data and Analytics Architectural Patterns](/sources/s15.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Stateless horizontally scaled inference**: Prediction components avoid durable serving state and scale by adding independent instances.
- **Asynchronous message-driven communication**: Uses non-blocking messaging and workload management between production components.
- **Geographic high availability and failover**: Distributing managed production operation across regions or continents for availability and automated failover.
