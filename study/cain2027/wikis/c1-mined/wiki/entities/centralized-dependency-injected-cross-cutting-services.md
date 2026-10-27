---
type: Design Alternative
title: Centralized dependency-injected cross-cutting services
description: Shared functionality spanning ML layers or pipelines is organized centrally and supplied to components through dependency injection rather than being independently implemented or configured in each component.
id: '47.3'
dimension: /concepts/ml-dependency-and-service-structure.md
accepted_by:
- s02_p15
- s16_p04
rejected_by: []
passages: 2
includes:
- Centralized dependency-injected cross-cutting services
tags:
- value
- accepted
- ml-dependency-and-service-structure
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Centralized dependency-injected cross-cutting services

Shared functionality spanning ML layers or pipelines is organized centrally and supplied to components through dependency injection rather than being independently implemented or configured in each component.

## Evidence

- **s02_p15** (accepts) · [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- **s16_p04** (accepts) · [Machine Learning in Production: Software Architecture](/sources/s16.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Centralized dependency-injected cross-cutting services**: Organizes shared cross-layer functionality centrally and supplies it through dependency injection.
