---
type: Design Decision
title: MLOps Platform Ownership and Sourcing
description: Who owns, operates, and supplies the infrastructure and platform used for MLOps.
id: '39'
core: false
values: 7
candidate_values: 4
outcomes: 3
evidence:
  codes: 13
  documents: 11
  sources: 4
relations: []
tags:
- dimension
exclusivity: 0.75
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# MLOps Platform Ownership and Sourcing

Who owns, operates, and supplies the infrastructure and platform used for MLOps.

## Values

| Value | Status | Passages |
|---|---|---|
| [Hybrid ML infrastructure operation](/entities/hybrid-ml-infrastructure-operation.md) | accepted | 4 |
| [Self-managed ML platform](/entities/self-managed-ml-platform.md) | accepted | 1 |
| [Dedicated internal ML operations team](/entities/dedicated-internal-ml-operations-team.md) | mixed | 2 |
| [In-house MLOps infrastructure](/entities/in-house-mlops-infrastructure.md) | mixed | 7 |
| [Hybrid-cloud management complexity](/entities/hybrid-cloud-management-complexity.md) | outcome | 1 |
| [Managed-platform compliance and security constraints](/entities/managed-platform-compliance-and-security-constraints.md) | outcome | 1 |
| [Specialist infrastructure skill requirement](/entities/specialist-infrastructure-skill-requirement.md) | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **3 of 4 sources** adopt one value (or a declared hybrid): exclusivity 0.75.

Values adopted together:

- [In-house MLOps infrastructure](/entities/in-house-mlops-infrastructure.md) and [Hybrid ML infrastructure operation](/entities/hybrid-ml-infrastructure-operation.md): [s21](/sources/s21.md)
- [In-house MLOps infrastructure](/entities/in-house-mlops-infrastructure.md) and [Self-managed ML platform](/entities/self-managed-ml-platform.md): [s21](/sources/s21.md)
- [Hybrid ML infrastructure operation](/entities/hybrid-ml-infrastructure-operation.md) and [Self-managed ML platform](/entities/self-managed-ml-platform.md): [s21](/sources/s21.md)

## Evidence

13 open codes from 11 passages in 4 sources.

**Core dimension:** no (4 sources; core = ≥ 9 sources).
