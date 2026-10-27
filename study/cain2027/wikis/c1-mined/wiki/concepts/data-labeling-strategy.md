---
type: Design Decision
title: Data Labeling Strategy
description: How labeled examples are produced and selected for supervised ML development.
id: '23'
core: false
values: 2
candidate_values: 2
outcomes: 0
evidence:
  codes: 8
  documents: 11
  sources: 5
relations: []
tags:
- dimension
exclusivity: 0.2
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Data Labeling Strategy

How labeled examples are produced and selected for supervised ML development.

## Values

| Value | Status | Passages |
|---|---|---|
| [Active-learning sample selection](/entities/active-learning-sample-selection.md) | accepted | 4 |
| [Human-in-the-loop data labeling](/entities/human-in-the-loop-data-labeling.md) | accepted | 10 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **1 of 5 sources** adopt one value (or a declared hybrid): exclusivity 0.20.

Values adopted together:

- [Human-in-the-loop data labeling](/entities/human-in-the-loop-data-labeling.md) and [Active-learning sample selection](/entities/active-learning-sample-selection.md): [s9](/sources/s9.md), [s10](/sources/s10.md), [s22](/sources/s22.md), [s24](/sources/s24.md)

## Evidence

8 open codes from 11 passages in 5 sources.

**Core dimension:** no (5 sources; core = ≥ 9 sources).
