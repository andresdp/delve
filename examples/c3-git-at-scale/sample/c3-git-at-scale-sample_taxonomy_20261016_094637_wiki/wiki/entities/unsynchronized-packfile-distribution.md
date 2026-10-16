---
type: Design Alternative
title: Unsynchronized packfile distribution
description: Pushed packfiles fan out without consensus because they are unreachable until references commit.
id: '30.12'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s01_p07
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Unsynchronized packfile distribution

Pushed packfiles fan out without consensus because they are unreachable until references commit.

## Evidence

- **s01_p07** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
