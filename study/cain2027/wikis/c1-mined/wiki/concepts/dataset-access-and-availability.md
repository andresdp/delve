---
type: Design Decision
title: Dataset Access and Availability
description: How datasets are exposed, extracted, sourced, materialized, and kept available to ML workflows.
id: '24'
core: true
values: 6
candidate_values: 5
outcomes: 1
evidence:
  codes: 12
  documents: 16
  sources: 12
relations: []
tags:
- dimension
- core
exclusivity: 0.6
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Dataset Access and Availability

How datasets are exposed, extracted, sourced, materialized, and kept available to ML workflows.

## Values

| Value | Status | Passages |
|---|---|---|
| [API-mediated dataset access](/entities/api-mediated-dataset-access.md) | accepted | 5 |
| [Data availability and throughput requirements](/entities/data-availability-and-throughput-requirements.md) | accepted | 4 |
| [External curated dataset sourcing](/entities/external-curated-dataset-sourcing.md) | accepted | 1 |
| [Local consolidation of external data](/entities/local-consolidation-of-external-data.md) | accepted | 3 |
| [Local sensitive-data storage](/entities/local-sensitive-data-storage.md) | mixed | 4 |
| [Online data-source availability requirement](/entities/online-data-source-availability-requirement.md) | outcome | 2 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **6 of 10 sources** adopt one value (or a declared hybrid): exclusivity 0.60.

Values adopted together:

- [API-mediated dataset access](/entities/api-mediated-dataset-access.md) and [Local consolidation of external data](/entities/local-consolidation-of-external-data.md): [s16](/sources/s16.md)
- [API-mediated dataset access](/entities/api-mediated-dataset-access.md) and [External curated dataset sourcing](/entities/external-curated-dataset-sourcing.md): [s24](/sources/s24.md)
- [API-mediated dataset access](/entities/api-mediated-dataset-access.md) and [Data availability and throughput requirements](/entities/data-availability-and-throughput-requirements.md): [s15](/sources/s15.md)
- [Local consolidation of external data](/entities/local-consolidation-of-external-data.md) and [Data availability and throughput requirements](/entities/data-availability-and-throughput-requirements.md): [s5](/sources/s5.md)

## Evidence

12 open codes from 16 passages in 12 sources.

**Core dimension:** yes ★ (12 sources; core = ≥ 9 sources).
