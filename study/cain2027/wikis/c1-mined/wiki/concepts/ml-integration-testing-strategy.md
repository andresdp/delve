---
type: Design Decision
title: ML Integration Testing Strategy
description: Varies how pipeline integration and production readiness are validated across components and environments.
id: '14'
core: true
values: 9
candidate_values: 9
outcomes: 0
evidence:
  codes: 34
  documents: 32
  sources: 14
relations: []
tags:
- dimension
- core
exclusivity: 0.36
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Integration Testing Strategy

Varies how pipeline integration and production readiness are validated across components and environments.

## Values

| Value | Status | Passages |
|---|---|---|
| [Automated data-and-model validation](/entities/automated-data-and-model-validation.md) | accepted | 9 |
| [Automated full-pipeline integration testing](/entities/automated-full-pipeline-integration-testing.md) | accepted | 12 |
| [Feature and model unit testing](/entities/feature-and-model-unit-testing.md) | accepted | 5 |
| [Prediction API contract testing](/entities/prediction-api-contract-testing.md) | accepted | 3 |
| [Prediction-service load and latency testing](/entities/prediction-service-load-and-latency-testing.md) | accepted | 2 |
| [Production canary validation](/entities/production-canary-validation.md) | accepted | 8 |
| [Schema and domain validation testing](/entities/schema-and-domain-validation-testing.md) | accepted | 2 |
| [Target-infrastructure compatibility testing](/entities/target-infrastructure-compatibility-testing.md) | accepted | 3 |
| [Training health validation](/entities/training-health-validation.md) | accepted | 5 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **5 of 14 sources** adopt one value (or a declared hybrid): exclusivity 0.36.

Values adopted together:

- [Automated full-pipeline integration testing](/entities/automated-full-pipeline-integration-testing.md) and [Production canary validation](/entities/production-canary-validation.md): [s6](/sources/s6.md), [s9](/sources/s9.md), [s13](/sources/s13.md), [s22](/sources/s22.md)
- [Automated full-pipeline integration testing](/entities/automated-full-pipeline-integration-testing.md) and [Feature and model unit testing](/entities/feature-and-model-unit-testing.md): [s6](/sources/s6.md), [s9](/sources/s9.md), [s22](/sources/s22.md), [s28](/sources/s28.md)
- [Automated full-pipeline integration testing](/entities/automated-full-pipeline-integration-testing.md) and [Automated data-and-model validation](/entities/automated-data-and-model-validation.md): [s6](/sources/s6.md), [s13](/sources/s13.md), [s21](/sources/s21.md), [s22](/sources/s22.md)
- [Production canary validation](/entities/production-canary-validation.md) and [Automated data-and-model validation](/entities/automated-data-and-model-validation.md): [s6](/sources/s6.md), [s13](/sources/s13.md), [s20](/sources/s20.md), [s22](/sources/s22.md)
- [Automated full-pipeline integration testing](/entities/automated-full-pipeline-integration-testing.md) and [Target-infrastructure compatibility testing](/entities/target-infrastructure-compatibility-testing.md): [s1](/sources/s1.md), [s6](/sources/s6.md), [s13](/sources/s13.md)
- 27 more pair(s)

## Evidence

34 open codes from 32 passages in 14 sources.

**Core dimension:** yes ★ (14 sources; core = ≥ 9 sources).
