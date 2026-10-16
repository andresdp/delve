---
type: Design Alternative
title: Orchestrated push fan-out
description: An orchestrator distributes pushed packfiles and reference transactions to repository instances.
id: '30.11'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s01_p07
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p003.md
- /designs/p020.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Orchestrated push fan-out

An orchestrator distributes pushed packfiles and reference transactions to repository instances.

## Evidence

- **s01_p07** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …

## In design points

[P003](/designs/p003.md), [P020](/designs/p020.md)
