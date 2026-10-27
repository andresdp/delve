---
type: Design Decision
title: Model Packaging and Runtime Placement
description: How models are packaged and placed into application, container, edge, or service runtimes.
id: '30'
core: true
values: 28
candidate_values: 24
outcomes: 4
evidence:
  codes: 106
  documents: 65
  sources: 22
relations: []
tags:
- dimension
- core
exclusivity: 0.29
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Model Packaging and Runtime Placement

How models are packaged and placed into application, container, edge, or service runtimes.

## Values

| Value | Status | Passages |
|---|---|---|
| [Amalgamated standalone model package](/entities/amalgamated-standalone-model-package.md) | accepted | 7 |
| [Automatic container image generation](/entities/automatic-container-image-generation.md) | accepted | 7 |
| [Client-server prediction architecture](/entities/client-server-prediction-architecture.md) | accepted | 1 |
| [Container-orchestrated ML runtime](/entities/container-orchestrated-ml-runtime.md) | accepted | 5 |
| [Containerized inference deployment](/entities/containerized-inference-deployment.md) | accepted | 4 |
| [Containerized offline prediction service](/entities/containerized-offline-prediction-service.md) | accepted | 6 |
| [Cross-format model serialization](/entities/cross-format-model-serialization.md) | accepted | 8 |
| [Hybrid microservice-monolith architecture](/entities/hybrid-microservice-monolith-architecture.md) | accepted | 5 |
| [Layered ML pipeline architecture](/entities/layered-ml-pipeline-architecture.md) | accepted | 6 |
| [Local deployment troubleshooting](/entities/local-deployment-troubleshooting.md) | accepted | 3 |
| [Long-running serving daemon](/entities/long-running-serving-daemon.md) | accepted | 2 |
| [Manually specified deployment image](/entities/manually-specified-deployment-image.md) | accepted | 4 |
| [Model-as-a-service deployment](/entities/model-as-a-service-deployment.md) | accepted | 16 |
| [Model-as-dependency deployment](/entities/model-as-dependency-deployment.md) | accepted | 10 |
| [Monolithic application architecture](/entities/monolithic-application-architecture.md) | accepted | 4 |
| [On-device edge inference](/entities/on-device-edge-inference.md) | accepted | 5 |
| [Plug-in model architecture](/entities/plug-in-model-architecture.md) | accepted | 1 |
| [Repository selection by workload](/entities/repository-selection-by-workload.md) | accepted | 2 |
| [Serverless zip-package deployment](/entities/serverless-zip-package-deployment.md) | accepted | 1 |
| [Client-side prediction placement](/entities/client-side-prediction-placement.md) | mixed | 1 |
| [Direct deployment of offline-trained model](/entities/direct-deployment-of-offline-trained-model.md) | mixed | 2 |
| [Microservice integration architecture](/entities/microservice-integration-architecture.md) | mixed | 13 |
| [Strict microservice deployment architecture](/entities/strict-microservice-deployment-architecture.md) | mixed | 3 |
| [Traditional Hadoop production architecture](/entities/traditional-hadoop-production-architecture.md) | rejected | 1 |
| [Independent component deployment outcome](/entities/independent-component-deployment-outcome.md) | outcome | 4 |
| [Interleaved model dependency outcome](/entities/interleaved-model-dependency-outcome.md) | outcome | 2 |
| [Serverless artifact-size constraint](/entities/serverless-artifact-size-constraint.md) | outcome | 1 |
| [Weak ML component boundaries outcome](/entities/weak-ml-component-boundaries-outcome.md) | outcome | 3 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **6 of 21 sources** adopt one value (or a declared hybrid): exclusivity 0.29.

Values adopted together:

- [Model-as-a-service deployment](/entities/model-as-a-service-deployment.md) and [Microservice integration architecture](/entities/microservice-integration-architecture.md): [s1](/sources/s1.md), [s4](/sources/s4.md), [s16](/sources/s16.md), [s19](/sources/s19.md), [s21](/sources/s21.md)
- [Model-as-a-service deployment](/entities/model-as-a-service-deployment.md) and [Model-as-dependency deployment](/entities/model-as-dependency-deployment.md): [s1](/sources/s1.md), [s9](/sources/s9.md), [s19](/sources/s19.md), [s21](/sources/s21.md), [s25](/sources/s25.md)
- [Model-as-a-service deployment](/entities/model-as-a-service-deployment.md) and [Amalgamated standalone model package](/entities/amalgamated-standalone-model-package.md): [s9](/sources/s9.md), [s19](/sources/s19.md), [s21](/sources/s21.md), [s25](/sources/s25.md)
- [Model-as-a-service deployment](/entities/model-as-a-service-deployment.md) and [Hybrid microservice-monolith architecture](/entities/hybrid-microservice-monolith-architecture.md): [s1](/sources/s1.md), [s13](/sources/s13.md), [s16](/sources/s16.md), [s20](/sources/s20.md)
- [Model-as-a-service deployment](/entities/model-as-a-service-deployment.md) and [Container-orchestrated ML runtime](/entities/container-orchestrated-ml-runtime.md): [s4](/sources/s4.md), [s6](/sources/s6.md), [s19](/sources/s19.md), [s25](/sources/s25.md)
- 126 more pair(s)

## Evidence

106 open codes from 65 passages in 22 sources.

**Core dimension:** yes ★ (22 sources; core = ≥ 9 sources).
