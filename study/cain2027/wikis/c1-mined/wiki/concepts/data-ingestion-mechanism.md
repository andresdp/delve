---
type: Design Decision
title: Data Ingestion Mechanism
description: How source events and records are delivered into ML data workflows.
id: '21'
core: false
values: 11
candidate_values: 9
outcomes: 2
evidence:
  codes: 30
  documents: 18
  sources: 8
relations:
- affects Training Execution and Scaling Strategy
- affects Production Monitoring and Adaptation
tags:
- dimension
exclusivity: 0.38
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Data Ingestion Mechanism

How source events and records are delivered into ML data workflows.

## Values

| Value | Status | Passages |
|---|---|---|
| [Change-data-capture ingestion](/entities/change-data-capture-ingestion.md) | accepted | 1 |
| [Dual-path event and data ingestion](/entities/dual-path-event-and-data-ingestion.md) | accepted | 4 |
| [ETL-based feature ingestion](/entities/etl-based-feature-ingestion.md) | accepted | 5 |
| [Event-stream data sourcing](/entities/event-stream-data-sourcing.md) | accepted | 3 |
| [Messaging-based data ingestion](/entities/messaging-based-data-ingestion.md) | accepted | 2 |
| [Push-based data delivery](/entities/push-based-data-delivery.md) | accepted | 2 |
| [Query-based data extraction](/entities/query-based-data-extraction.md) | accepted | 3 |
| [Raw-dump data sourcing](/entities/raw-dump-data-sourcing.md) | accepted | 2 |
| [Streaming feature ingestion](/entities/streaming-feature-ingestion.md) | accepted | 13 |
| [Event-stream historical-retention limitation](/entities/event-stream-historical-retention-limitation.md) | outcome | 1 |
| [Raw-schema coupling and pipeline fragility](/entities/raw-schema-coupling-and-pipeline-fragility.md) | outcome | 1 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Training Execution and Scaling Strategy](/concepts/training-execution-and-scaling-strategy.md). *Ingestion mode, feature transformations, and available datasets determine training inputs, freshness, and execution requirements.*
- Choices on this dimension affect the outcomes of [Production Monitoring and Adaptation](/concepts/production-monitoring-and-adaptation.md). *Feature-generation frequency and incoming-data changes affect model behavior and retraining needs.*

### To this dimension

- [ML Workflow Execution Coordination](/concepts/ml-workflow-execution-coordination.md) requires this dimension to be decided first. *Workflow stages must be defined around the data-ingestion and feature-preparation steps they execute.*

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **3 of 8 sources** adopt one value (or a declared hybrid): exclusivity 0.38.

Values adopted together:

- [ETL-based feature ingestion](/entities/etl-based-feature-ingestion.md) and [Streaming feature ingestion](/entities/streaming-feature-ingestion.md): [s2](/sources/s2.md), [s4](/sources/s4.md), [s5](/sources/s5.md), [s15](/sources/s15.md)
- [Streaming feature ingestion](/entities/streaming-feature-ingestion.md) and [Dual-path event and data ingestion](/entities/dual-path-event-and-data-ingestion.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s15](/sources/s15.md)
- [ETL-based feature ingestion](/entities/etl-based-feature-ingestion.md) and [Dual-path event and data ingestion](/entities/dual-path-event-and-data-ingestion.md): [s2](/sources/s2.md), [s15](/sources/s15.md)
- [ETL-based feature ingestion](/entities/etl-based-feature-ingestion.md) and [Messaging-based data ingestion](/entities/messaging-based-data-ingestion.md): [s2](/sources/s2.md), [s15](/sources/s15.md)
- [ETL-based feature ingestion](/entities/etl-based-feature-ingestion.md) and [Push-based data delivery](/entities/push-based-data-delivery.md): [s4](/sources/s4.md), [s15](/sources/s15.md)
- 25 more pair(s)

## Evidence

30 open codes from 18 passages in 8 sources.

**Core dimension:** no (8 sources; core = ≥ 9 sources).
