---
type: Design Decision
title: Runtime State and Communication Strategy
description: How serving and training components maintain state, communicate, queue work, and provide availability.
id: '25'
core: true
values: 6
candidate_values: 5
outcomes: 1
evidence:
  codes: 35
  documents: 20
  sources: 11
relations:
- affects Model Evaluation and Regression Strategy
- requires Model Serving Interface
tags:
- dimension
- core
exclusivity: 1.0
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Runtime State and Communication Strategy

How serving and training components maintain state, communicate, queue work, and provide availability.

## Values

| Value | Status | Passages |
|---|---|---|
| [Asynchronous message-driven serving](/entities/asynchronous-message-driven-serving.md) | accepted | 4 |
| [Atomic distributed stateful serving](/entities/atomic-distributed-stateful-serving.md) | accepted | 5 |
| [Geographically redundant asynchronous serving](/entities/geographically-redundant-asynchronous-serving.md) | accepted | 4 |
| [Horizontally scaled Redis-backed asynchronous serving](/entities/horizontally-scaled-redis-backed-asynchronous-serving.md) | accepted | 5 |
| [Stateless horizontally scaled serving](/entities/stateless-horizontally-scaled-serving.md) | accepted | 2 |
| [Query latency-consistency trade-off](/entities/query-latency-consistency-trade-off.md) | outcome | 1 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- Choices on this dimension affect the outcomes of [Model Evaluation and Regression Strategy](/concepts/model-evaluation-and-regression-strategy.md). *Runtime resource and state choices influence latency, throughput, compatibility, and the feasibility of production tests.*
- This dimension requires [Model Serving Interface](/concepts/model-serving-interface.md) to be decided first. *State stores, queues, and scaling policies are selected after the deployment topology and serving mode are established.*

### To this dimension

- Choices on [Training Execution and Scaling Strategy](/concepts/training-execution-and-scaling-strategy.md) limit the options available on this dimension. *Training scale and memory behavior determine suitable hardware, state handling, and resource allocation.*
- Choices on [Model Family and Combination Strategy](/concepts/model-family-and-combination-strategy.md) affect the outcomes of this dimension. *Model complexity and prediction representation influence serving memory, latency, and hardware requirements.*

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **11 of 11 sources** adopt one value (or a declared hybrid): exclusivity 1.00.

## Evidence

35 open codes from 20 passages in 11 sources.

**Core dimension:** yes ★ (11 sources; core = ≥ 9 sources).
