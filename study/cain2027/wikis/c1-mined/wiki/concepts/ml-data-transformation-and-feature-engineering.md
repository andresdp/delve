---
type: Design Decision
title: ML Data Transformation and Feature Engineering
description: How data is preprocessed, transformed, engineered into features, reused, and retired for ML workflows.
id: '41'
core: true
values: 6
candidate_values: 5
outcomes: 1
evidence:
  codes: 25
  documents: 28
  sources: 15
relations: []
tags:
- dimension
- core
exclusivity: 0.23
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Data Transformation and Feature Engineering

How data is preprocessed, transformed, engineered into features, reused, and retired for ML workflows.

## Values

| Value | Status | Passages |
|---|---|---|
| [Automated data preprocessing](/entities/automated-data-preprocessing.md) | accepted | 11 |
| [Automated feature engineering](/entities/automated-feature-engineering.md) | accepted | 11 |
| [Denormalized or aggregated training dataset](/entities/denormalized-or-aggregated-training-dataset.md) | accepted | 7 |
| [Feature lifecycle cleanup](/entities/feature-lifecycle-cleanup.md) | accepted | 3 |
| [Shared data-processing pipeline reuse](/entities/shared-data-processing-pipeline-reuse.md) | mixed | 7 |
| [Duplicated data-processing pipelines](/entities/duplicated-data-processing-pipelines.md) | outcome | 3 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **3 of 13 sources** adopt one value (or a declared hybrid): exclusivity 0.23.

Values adopted together:

- [Automated data preprocessing](/entities/automated-data-preprocessing.md) and [Automated feature engineering](/entities/automated-feature-engineering.md): [s2](/sources/s2.md), [s9](/sources/s9.md), [s17](/sources/s17.md), [s18](/sources/s18.md), [s19](/sources/s19.md)
- [Denormalized or aggregated training dataset](/entities/denormalized-or-aggregated-training-dataset.md) and [Automated data preprocessing](/entities/automated-data-preprocessing.md): [s4](/sources/s4.md), [s9](/sources/s9.md), [s19](/sources/s19.md), [s24](/sources/s24.md)
- [Automated data preprocessing](/entities/automated-data-preprocessing.md) and [Feature lifecycle cleanup](/entities/feature-lifecycle-cleanup.md): [s18](/sources/s18.md), [s19](/sources/s19.md), [s22](/sources/s22.md)
- [Automated data preprocessing](/entities/automated-data-preprocessing.md) and [Shared data-processing pipeline reuse](/entities/shared-data-processing-pipeline-reuse.md): [s2](/sources/s2.md), [s13](/sources/s13.md), [s19](/sources/s19.md)
- [Automated feature engineering](/entities/automated-feature-engineering.md) and [Shared data-processing pipeline reuse](/entities/shared-data-processing-pipeline-reuse.md): [s2](/sources/s2.md), [s10](/sources/s10.md), [s19](/sources/s19.md)
- 5 more pair(s)

## Evidence

25 open codes from 28 passages in 15 sources.

**Core dimension:** yes ★ (15 sources; core = ≥ 9 sources).
