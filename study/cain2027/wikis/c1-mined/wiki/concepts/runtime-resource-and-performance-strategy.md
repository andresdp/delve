---
type: Design Decision
title: Runtime Resource and Performance Strategy
description: How ML workloads allocate compute resources and meet scaling, latency, and cost constraints.
id: '26'
core: true
values: 17
candidate_values: 9
outcomes: 8
evidence:
  codes: 35
  documents: 31
  sources: 15
relations: []
tags:
- dimension
- core
exclusivity: 0.42
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Runtime Resource and Performance Strategy

How ML workloads allocate compute resources and meet scaling, latency, and cost constraints.

## Values

| Value | Status | Passages |
|---|---|---|
| [CPU-or-GPU resource allocation](/entities/cpu-or-gpu-resource-allocation.md) | accepted | 3 |
| [Compute-optimized training hardware](/entities/compute-optimized-training-hardware.md) | accepted | 4 |
| [Elastic resource scaling](/entities/elastic-resource-scaling.md) | accepted | 7 |
| [Large-scale data processing capacity](/entities/large-scale-data-processing-capacity.md) | accepted | 5 |
| [ONNX inference optimization](/entities/onnx-inference-optimization.md) | accepted | 2 |
| [Scale-to-zero serving](/entities/scale-to-zero-serving.md) | accepted | 3 |
| [Service resource and latency profiling](/entities/service-resource-and-latency-profiling.md) | accepted | 3 |
| [Replicated mutable model instances](/entities/replicated-mutable-model-instances.md) | mixed | 2 |
| [Full-dataset in-memory retention](/entities/full-dataset-in-memory-retention.md) | rejected | 1 |
| [Application hosting and development cost](/entities/application-hosting-and-development-cost.md) | outcome | 1 |
| [CPU and memory sizing guidance](/entities/cpu-and-memory-sizing-guidance.md) | outcome | 1 |
| [Extended fraud-decision latency](/entities/extended-fraud-decision-latency.md) | outcome | 2 |
| [ML infrastructure delivery time](/entities/ml-infrastructure-delivery-time.md) | outcome | 3 |
| [ML infrastructure investment cost](/entities/ml-infrastructure-investment-cost.md) | outcome | 5 |
| [Nano-scale endpoint resource constraints](/entities/nano-scale-endpoint-resource-constraints.md) | outcome | 2 |
| [ONNX performance improvement](/entities/onnx-performance-improvement.md) | outcome | 1 |
| [Sub-10-millisecond scoring latency](/entities/sub-10-millisecond-scoring-latency.md) | outcome | 7 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **5 of 12 sources** adopt one value (or a declared hybrid): exclusivity 0.42.

Values adopted together:

- [Elastic resource scaling](/entities/elastic-resource-scaling.md) and [Large-scale data processing capacity](/entities/large-scale-data-processing-capacity.md): [s2](/sources/s2.md), [s4](/sources/s4.md), [s21](/sources/s21.md)
- [Compute-optimized training hardware](/entities/compute-optimized-training-hardware.md) and [Service resource and latency profiling](/entities/service-resource-and-latency-profiling.md): [s4](/sources/s4.md), [s25](/sources/s25.md)
- [CPU-or-GPU resource allocation](/entities/cpu-or-gpu-resource-allocation.md) and [Elastic resource scaling](/entities/elastic-resource-scaling.md): [s4](/sources/s4.md), [s13](/sources/s13.md)
- [Compute-optimized training hardware](/entities/compute-optimized-training-hardware.md) and [Scale-to-zero serving](/entities/scale-to-zero-serving.md): [s11](/sources/s11.md)
- [Compute-optimized training hardware](/entities/compute-optimized-training-hardware.md) and [CPU-or-GPU resource allocation](/entities/cpu-or-gpu-resource-allocation.md): [s4](/sources/s4.md)
- 11 more pair(s)

## Evidence

35 open codes from 31 passages in 15 sources.

**Core dimension:** yes ★ (15 sources; core = ≥ 9 sources).
