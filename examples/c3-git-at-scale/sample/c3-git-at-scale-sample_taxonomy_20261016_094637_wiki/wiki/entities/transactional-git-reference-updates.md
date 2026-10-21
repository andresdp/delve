---
type: Design Alternative
title: Transactional Git reference updates
description: Git reference mutations use atomic, validated transactions that produce deterministic results and roll back completely on failure.
id: '30.3'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s01_p07
- s02_p04
rejected_by: []
passages: 2
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

# Transactional Git reference updates

Git reference mutations use atomic, validated transactions that produce deterministic results and roll back completely on failure.

## Evidence

- **s01_p07** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s02_p04** (accepts) · [Stretching Spokes](/sources/s2.md) · Git reference update transactions
  > Three-phase commit is a core part of keeping the replicas in sync. Implementing it requires each of the replicas to be able to answer the question “can you carry out the following reference updates?”, and then to either commit or roll back the transaction based on the coordinator’s instructions. To make this possible, we implemented transactions for Git reference updates …
