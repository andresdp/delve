---
type: Design Decision
title: Replica Topology
description: How many repository replicas are maintained, and what replica-count structure is used?
id: '21'
core: true
values: 3
candidate_values: 2
outcomes: 1
evidence:
  codes: 6
  documents: 11
  sources: 3
relations: []
tags:
- dimension
- core
exclusivity: 1.0
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-spokes.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica Topology

How many repository replicas are maintained, and what replica-count structure is used?

## Values

| Value | Status | Passages |
|---|---|---|
| [Three-replica repository replication](/entities/three-replica-repository-replication.md) | accepted | 9 |
| [Single-extra-copy replication](/entities/single-extra-copy-replication.md) | rejected | 2 |
| [Idle-replica resource overhead](/entities/idle-replica-resource-overhead.md) | outcome | 3 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **2 of 2 systems** adopt one value (or a declared hybrid): exclusivity 1.00.

## Evidence

6 open codes from 11 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 2 systems; core = ≥ 2 sources or ≥ 2 systems).
