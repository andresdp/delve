---
title: Reference-update amplification
type: value
id: '30.16'
status: outcome
dimension: '[[concepts/replica-write-coordination|Replica Write Coordination]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-write-coordination
---

# Reference-update amplification

Pull-request bookkeeping can multiply one user push into many additional replicated reference updates.

## Evidence

- **s02_p02** (supports) · [[sources/s2|Stretching Spokes]] · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
