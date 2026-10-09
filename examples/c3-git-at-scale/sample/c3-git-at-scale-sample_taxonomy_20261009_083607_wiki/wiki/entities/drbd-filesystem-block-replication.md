---
title: DRBD filesystem block replication
type: value
id: '1.8'
status: mixed
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by:
- s02_p02
rejected_by:
- s02_p02
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- mixed
- repository-replica-placement
---

# DRBD filesystem block replication

Use latency-sensitive filesystem block replication with replicas kept colocated.

## Evidence

- **s02_p02** (both) · [[sources/s2|Stretching Spokes]] · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
