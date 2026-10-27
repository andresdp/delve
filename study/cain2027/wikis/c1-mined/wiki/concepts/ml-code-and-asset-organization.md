---
type: Design Decision
title: ML Code and Asset Organization
description: How ML code, reusable assets, documentation, and production structure are organized.
id: '46'
core: true
values: 13
candidate_values: 7
outcomes: 6
evidence:
  codes: 25
  documents: 28
  sources: 16
relations: []
tags:
- dimension
- core
exclusivity: 0.58
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# ML Code and Asset Organization

How ML code, reusable assets, documentation, and production structure are organized.

## Values

| Value | Status | Passages |
|---|---|---|
| [Deployable and understandable model code](/entities/deployable-and-understandable-model-code.md) | accepted | 6 |
| [Object-oriented production code organization](/entities/object-oriented-production-code-organization.md) | accepted | 4 |
| [Collaborative reusable asset development](/entities/collaborative-reusable-asset-development.md) | mixed | 8 |
| [Disconnected script-based asset organization](/entities/disconnected-script-based-asset-organization.md) | mixed | 2 |
| [Ad hoc asset documentation](/entities/ad-hoc-asset-documentation.md) | rejected | 1 |
| [Complex mixed technology stack](/entities/complex-mixed-technology-stack.md) | rejected | 3 |
| [Poor-quality data-science code](/entities/poor-quality-data-science-code.md) | rejected | 2 |
| [Data-scientist-only usability problems](/entities/data-scientist-only-usability-problems.md) | outcome | 4 |
| [Generated model-development workflow](/entities/generated-model-development-workflow.md) | outcome | 2 |
| [Knowledge continuity after contributor departure](/entities/knowledge-continuity-after-contributor-departure.md) | outcome | 1 |
| [ML engineering tooling gap](/entities/ml-engineering-tooling-gap.md) | outcome | 3 |
| [Reduced ML expertise dependence](/entities/reduced-ml-expertise-dependence.md) | outcome | 3 |
| [Undocumented unnecessary functionality](/entities/undocumented-unnecessary-functionality.md) | outcome | 2 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **7 of 12 sources** adopt one value (or a declared hybrid): exclusivity 0.58.

Values adopted together:

- [Deployable and understandable model code](/entities/deployable-and-understandable-model-code.md) and [Collaborative reusable asset development](/entities/collaborative-reusable-asset-development.md): [s13](/sources/s13.md), [s18](/sources/s18.md), [s19](/sources/s19.md)
- [Object-oriented production code organization](/entities/object-oriented-production-code-organization.md) and [Collaborative reusable asset development](/entities/collaborative-reusable-asset-development.md): [s26](/sources/s26.md)
- [Deployable and understandable model code](/entities/deployable-and-understandable-model-code.md) and [Disconnected script-based asset organization](/entities/disconnected-script-based-asset-organization.md): [s22](/sources/s22.md)

## Evidence

25 open codes from 28 passages in 16 sources.

**Core dimension:** yes ★ (16 sources; core = ≥ 9 sources).
