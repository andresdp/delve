---
type: Design Decision
title: Model Serving Interface
description: How deployed models expose prediction interfaces and exchange model inputs and outputs.
id: '29'
core: true
values: 8
candidate_values: 8
outcomes: 0
evidence:
  codes: 35
  documents: 37
  sources: 17
relations: []
tags:
- dimension
- core
exclusivity: 0.53
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Model Serving Interface

How deployed models expose prediction interfaces and exchange model inputs and outputs.

## Values

| Value | Status | Passages |
|---|---|---|
| [Cross-service identifier translation](/entities/cross-service-identifier-translation.md) | accepted | 1 |
| [Multi-source model input interface](/entities/multi-source-model-input-interface.md) | accepted | 6 |
| [PMML-based model serving](/entities/pmml-based-model-serving.md) | accepted | 7 |
| [Parallelized service data access](/entities/parallelized-service-data-access.md) | accepted | 6 |
| [REST prediction microservice](/entities/rest-prediction-microservice.md) | accepted | 22 |
| [Socket-based model interface](/entities/socket-based-model-interface.md) | accepted | 2 |
| [gRPC model interface](/entities/grpc-model-interface.md) | accepted | 2 |
| [Adoption of external service identifiers](/entities/adoption-of-external-service-identifiers.md) | mixed | 1 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### To this dimension

- [Runtime State and Communication Strategy](/concepts/runtime-state-and-communication-strategy.md) requires this dimension to be decided first. *State stores, queues, and scaling policies are selected after the deployment topology and serving mode are established.*

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **9 of 17 sources** adopt one value (or a declared hybrid): exclusivity 0.53.

Values adopted together:

- [REST prediction microservice](/entities/rest-prediction-microservice.md) and [Parallelized service data access](/entities/parallelized-service-data-access.md): [s9](/sources/s9.md), [s10](/sources/s10.md), [s16](/sources/s16.md)
- [REST prediction microservice](/entities/rest-prediction-microservice.md) and [PMML-based model serving](/entities/pmml-based-model-serving.md): [s10](/sources/s10.md), [s19](/sources/s19.md)
- [REST prediction microservice](/entities/rest-prediction-microservice.md) and [Multi-source model input interface](/entities/multi-source-model-input-interface.md): [s2](/sources/s2.md), [s9](/sources/s9.md)
- [REST prediction microservice](/entities/rest-prediction-microservice.md) and [gRPC model interface](/entities/grpc-model-interface.md): [s19](/sources/s19.md), [s21](/sources/s21.md)
- [REST prediction microservice](/entities/rest-prediction-microservice.md) and [Socket-based model interface](/entities/socket-based-model-interface.md): [s16](/sources/s16.md), [s19](/sources/s19.md)
- 14 more pair(s)

## Evidence

35 open codes from 37 passages in 17 sources.

**Core dimension:** yes ★ (17 sources; core = ≥ 9 sources).
