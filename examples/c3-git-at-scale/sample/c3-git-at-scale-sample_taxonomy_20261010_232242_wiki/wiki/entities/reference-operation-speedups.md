---
title: Reference-operation speedups
type: value
id: '11.41'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s02_p04
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Reference-operation speedups

Reference operations are optimized to reduce per-replica update time.

## Evidence

- **s02_p04** (accepts) · [[sources/s2|Stretching Spokes]] · Git reference update transactions
  > Three-phase commit is a core part of keeping the replicas in sync. Implementing it requires each of the replicas to be able to answer the question “can you carry out the following reference updates?”, and then to either commit or roll back the transaction based on the coordinator’s instructions. To make this possible, we implemented transactions for Git reference updates …
