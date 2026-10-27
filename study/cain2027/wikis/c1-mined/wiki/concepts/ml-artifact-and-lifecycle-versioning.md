---
type: Design Decision
title: ML Artifact and Lifecycle Versioning
description: How ML artifacts, experiments, runs, metadata, and deployment health are versioned and governed.
id: '20'
core: true
values: 7
candidate_values: 6
outcomes: 1
evidence:
  codes: 175
  documents: 37
  sources: 12
relations: []
tags:
- dimension
- core
exclusivity: 1.0
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Artifact and Lifecycle Versioning

How ML artifacts, experiments, runs, metadata, and deployment health are versioned and governed.

## Values

| Value | Status | Passages |
|---|---|---|
| [Artifact version control](/entities/artifact-version-control.md) | accepted | 2 |
| [Comprehensive ML lifecycle traceability](/entities/comprehensive-ml-lifecycle-traceability.md) | accepted | 8 |
| [Data-to-model lineage management](/entities/data-to-model-lineage-management.md) | accepted | 4 |
| [End-to-end reproducible lifecycle governance](/entities/end-to-end-reproducible-lifecycle-governance.md) | accepted | 10 |
| [Pipeline and experiment version control](/entities/pipeline-and-experiment-version-control.md) | accepted | 6 |
| [Pipeline-based CI/CD governance](/entities/pipeline-based-ci-cd-governance.md) | accepted | 5 |
| [Experiment reproducibility difficulty](/entities/experiment-reproducibility-difficulty.md) | outcome | 3 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **12 of 12 sources** adopt one value (or a declared hybrid): exclusivity 1.00.

## Evidence

175 open codes from 37 passages in 12 sources.

**Core dimension:** yes ★ (12 sources; core = ≥ 9 sources).
