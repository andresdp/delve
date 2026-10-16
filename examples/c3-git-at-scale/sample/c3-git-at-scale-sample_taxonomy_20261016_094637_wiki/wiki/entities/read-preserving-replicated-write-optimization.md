---
type: Design Alternative
title: Read-preserving replicated-write optimization
description: Replication write acceleration is designed without degrading the much more frequent repository reads.
id: '30.14'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s02_p02
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

# Read-preserving replicated-write optimization

Replication write acceleration is designed without degrading the much more frequent repository reads.

## Evidence

- **s02_p02** (accepts) · [Stretching Spokes](/sources/s2.md) · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
- **s02_p04** (accepts) · [Stretching Spokes](/sources/s2.md) · Git reference update transactions
  > Three-phase commit is a core part of keeping the replicas in sync. Implementing it requires each of the replicas to be able to answer the question “can you carry out the following reference updates?”, and then to either commit or roll back the transaction based on the coordinator’s instructions. To make this possible, we implemented transactions for Git reference updates …
