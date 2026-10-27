---
type: Design Decision
title: ML Release Automation
description: How ML code, pipelines, and environments are automatically built, tested, and released.
id: '19'
core: true
values: 5
candidate_values: 5
outcomes: 0
evidence:
  codes: 109
  documents: 33
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

# ML Release Automation

How ML code, pipelines, and environments are automatically built, tested, and released.

## Values

| Value | Status | Passages |
|---|---|---|
| [Commit-triggered staged release automation](/entities/commit-triggered-staged-release-automation.md) | accepted | 8 |
| [Environment-gated deployment automation](/entities/environment-gated-deployment-automation.md) | accepted | 2 |
| [Progressive release automation with rollback](/entities/progressive-release-automation-with-rollback.md) | accepted | 8 |
| [Recovery-oriented release automation with manual intervention](/entities/recovery-oriented-release-automation-with-manual-intervention.md) | accepted | 9 |
| [Unified release automation](/entities/unified-release-automation.md) | accepted | 6 |

## Exclusivity

The values of a dimension are alternatives, so each source should adopt one of them. **12 of 12 sources** adopt one value (or a declared hybrid): exclusivity 1.00.

## Evidence

109 open codes from 33 passages in 12 sources.

**Core dimension:** yes ★ (12 sources; core = ≥ 9 sources).
