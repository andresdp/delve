---
type: Outcome
title: Reference-update amplification
description: Pull-request bookkeeping can multiply one user push into many additional replicated reference updates.
id: '30.16'
dimension: /concepts/replica-write-coordination.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- outcome
- replica-write-coordination
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Reference-update amplification

Pull-request bookkeeping can multiply one user push into many additional replicated reference updates.

## Evidence

- **s02_p02** (supports) · [Stretching Spokes](/sources/s2.md) · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
