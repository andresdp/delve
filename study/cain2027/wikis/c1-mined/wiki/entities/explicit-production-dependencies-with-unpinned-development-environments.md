---
type: Design Alternative
title: Explicit production dependencies with unpinned development environments
description: Production dependencies are declared, while notebook or model-development environments may rely on library versions that are not explicitly pinned across machines.
id: '47.2'
dimension: /concepts/ml-dependency-and-service-structure.md
accepted_by:
- s09_p10
- s29_p06
rejected_by: []
passages: 2
includes:
- Production dependency and environment specification
- Unpinned environment dependencies
tags:
- value
- accepted
- ml-dependency-and-service-structure
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Explicit production dependencies with unpinned development environments

Production dependencies are declared, while notebook or model-development environments may rely on library versions that are not explicitly pinned across machines.

## Evidence

- **s09_p10** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)
- **s29_p06** (accepts) · [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Production dependency and environment specification**: Declares packages, images, and runtime resources required for production execution.
- **Unpinned environment dependencies**: Allowing notebook or model environments to rely on library versions that are not explicitly pinned across machines.
