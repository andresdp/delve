---
type: Design Decision
title: ML Dependency and Service Structure
description: How ML dependencies and cross-cutting services are specified, injected, and reproduced across environments.
id: '47'
core: false
values: 4
candidate_values: 3
outcomes: 1
evidence:
  codes: 14
  documents: 11
  sources: 8
relations: []
tags:
- dimension
exclusivity: 1.0
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Dependency and Service Structure

How ML dependencies and cross-cutting services are specified, injected, and reproduced across environments.

## Values

| Value | Status | Passages |
|---|---|---|
| [Centralized dependency-injected cross-cutting services](/entities/centralized-dependency-injected-cross-cutting-services.md) | accepted | 2 |
| [Explicit production dependencies with unpinned development environments](/entities/explicit-production-dependencies-with-unpinned-development-environments.md) | accepted | 2 |
| [Explicitly specified production dependencies](/entities/explicitly-specified-production-dependencies.md) | accepted | 3 |
| [Dependency reproducibility concern](/entities/dependency-reproducibility-concern.md) | outcome | 5 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **7 of 7 sources** adopt one value (or a declared hybrid): exclusivity 1.00.

## Evidence

14 open codes from 11 passages in 8 sources.

**Core dimension:** no (8 sources; core = ≥ 9 sources).
