---
type: Design Decision
title: ML Feature and Data Serving Storage
description: How prepared ML data and features are stored and served to training or inference components.
id: '43'
core: true
values: 5
candidate_values: 4
outcomes: 1
evidence:
  codes: 89
  documents: 25
  sources: 14
relations: []
tags:
- dimension
- core
exclusivity: 1.0
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Feature and Data Serving Storage

How prepared ML data and features are stored and served to training or inference components.

## Values

| Value | Status | Passages |
|---|---|---|
| [Central analytical ML data platform](/entities/central-analytical-ml-data-platform.md) | accepted | 6 |
| [Durable end-to-end feature platform](/entities/durable-end-to-end-feature-platform.md) | accepted | 7 |
| [Online feature-serving pipeline](/entities/online-feature-serving-pipeline.md) | accepted | 8 |
| [Online/offline feature-store architecture](/entities/online-offline-feature-store-architecture.md) | accepted | 2 |
| [Distributed feature-retrieval architecture outcome](/entities/distributed-feature-retrieval-architecture-outcome.md) | outcome | 3 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **14 of 14 sources** adopt one value (or a declared hybrid): exclusivity 1.00.

## Evidence

89 open codes from 25 passages in 14 sources.

**Core dimension:** yes ★ (14 sources; core = ≥ 9 sources).
