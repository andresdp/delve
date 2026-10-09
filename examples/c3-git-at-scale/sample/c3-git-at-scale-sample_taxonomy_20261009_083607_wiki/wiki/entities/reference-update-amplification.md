---
title: Reference-update amplification
type: value
id: '2.39'
status: outcome
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- write-coordination-and-replica-consistency
---

# Reference-update amplification

Internal pull-request and testing workflows multiply one user push into many reference updates.

## Evidence

- **s02_p02** (supports) · [[sources/s2|Stretching Spokes]] · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
