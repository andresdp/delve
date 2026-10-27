---
type: Design Decision
title: ML Workflow Execution Coordination
description: How ML workflow steps are automated, ordered, parallelized, and structured during execution.
id: '32'
core: true
values: 3
candidate_values: 2
outcomes: 1
evidence:
  codes: 29
  documents: 31
  sources: 14
relations:
- requires Data Ingestion Mechanism
tags:
- dimension
- core
exclusivity: 0.71
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Workflow Execution Coordination

How ML workflow steps are automated, ordered, parallelized, and structured during execution.

## Values

| Value | Status | Passages |
|---|---|---|
| [Manual script-driven workflow](/entities/manual-script-driven-workflow.md) | accepted | 7 |
| [Orchestrated ML pipeline](/entities/orchestrated-ml-pipeline.md) | accepted | 24 |
| [Rigid Hadoop processing workflow](/entities/rigid-hadoop-processing-workflow.md) | outcome | 1 |

## Relations

How to read them: [Relations between dimensions](/relations.md).

### From this dimension

- This dimension requires [Data Ingestion Mechanism](/concepts/data-ingestion-mechanism.md) to be decided first. *Workflow stages must be defined around the data-ingestion and feature-preparation steps they execute.*

### To this dimension

- [Model Evaluation and Regression Strategy](/concepts/model-evaluation-and-regression-strategy.md) requires this dimension to be decided first. *Automated integration, regression, and canary checks depend on the workflow and release path being established.*

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **10 of 14 sources** adopt one value (or a declared hybrid): exclusivity 0.71.

Values adopted together:

- [Manual script-driven workflow](/entities/manual-script-driven-workflow.md) and [Orchestrated ML pipeline](/entities/orchestrated-ml-pipeline.md): [s4](/sources/s4.md), [s9](/sources/s9.md), [s20](/sources/s20.md), [s21](/sources/s21.md)

## Evidence

29 open codes from 31 passages in 14 sources.

**Core dimension:** yes ★ (14 sources; core = ≥ 9 sources).
