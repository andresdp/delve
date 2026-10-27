---
type: Design Decision
title: Prediction Serving Mode and Performance
description: When and how predictions are computed, delivered, persisted, recovered, and kept fresh in production.
id: '31'
core: true
values: 17
candidate_values: 13
outcomes: 4
evidence:
  codes: 64
  documents: 43
  sources: 15
relations: []
tags:
- dimension
- core
exclusivity: 0.2
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Prediction Serving Mode and Performance

When and how predictions are computed, delivered, persisted, recovered, and kept fresh in production.

## Values

| Value | Status | Passages |
|---|---|---|
| [Candidate-user assignment](/entities/candidate-user-assignment.md) | accepted | 2 |
| [Hybrid offline-online serving](/entities/hybrid-offline-online-serving.md) | accepted | 5 |
| [Offline-online serving parity](/entities/offline-online-serving-parity.md) | accepted | 6 |
| [Online computation serving](/entities/online-computation-serving.md) | accepted | 15 |
| [Precomputed offline serving](/entities/precomputed-offline-serving.md) | accepted | 10 |
| [Precomputed-result fallback](/entities/precomputed-result-fallback.md) | accepted | 4 |
| [Prediction-serving fallback behavior](/entities/prediction-serving-fallback-behavior.md) | accepted | 4 |
| [Production prediction persistence](/entities/production-prediction-persistence.md) | accepted | 6 |
| [Queue-fronted online serving cluster](/entities/queue-fronted-online-serving-cluster.md) | accepted | 4 |
| [Report-based result delivery](/entities/report-based-result-delivery.md) | accepted | 6 |
| [Scheduled batch prediction deployment](/entities/scheduled-batch-prediction-deployment.md) | accepted | 10 |
| [Serverless function deployment](/entities/serverless-function-deployment.md) | accepted | 9 |
| [Threshold-based prediction decision](/entities/threshold-based-prediction-decision.md) | accepted | 3 |
| [Nearline computation serving](/entities/nearline-computation-serving.md) | outcome | 3 |
| [Probability-valued prediction output](/entities/probability-valued-prediction-output.md) | outcome | 3 |
| [Real-time recommendation infeasibility](/entities/real-time-recommendation-infeasibility.md) | outcome | 1 |
| [Recommendation-result staleness](/entities/recommendation-result-staleness.md) | outcome | 2 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **3 of 15 sources** adopt one value (or a declared hybrid): exclusivity 0.20.

Values adopted together:

- [Scheduled batch prediction deployment](/entities/scheduled-batch-prediction-deployment.md) and [Online computation serving](/entities/online-computation-serving.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s15](/sources/s15.md), [s19](/sources/s19.md)
- [Queue-fronted online serving cluster](/entities/queue-fronted-online-serving-cluster.md) and [Scheduled batch prediction deployment](/entities/scheduled-batch-prediction-deployment.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s19](/sources/s19.md)
- [Queue-fronted online serving cluster](/entities/queue-fronted-online-serving-cluster.md) and [Online computation serving](/entities/online-computation-serving.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s19](/sources/s19.md)
- [Queue-fronted online serving cluster](/entities/queue-fronted-online-serving-cluster.md) and [Precomputed offline serving](/entities/precomputed-offline-serving.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s19](/sources/s19.md)
- [Queue-fronted online serving cluster](/entities/queue-fronted-online-serving-cluster.md) and [Offline-online serving parity](/entities/offline-online-serving-parity.md): [s2](/sources/s2.md), [s12](/sources/s12.md), [s19](/sources/s19.md)
- 58 more pair(s)

## Evidence

64 open codes from 43 passages in 15 sources.

**Core dimension:** yes ★ (15 sources; core = ≥ 9 sources).
