---
title: Operation-failure-based primary failure detection
type: value
id: '3.14'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p04
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Operation-failure-based primary failure detection

Detect replica failure from failed repository operations rather than heartbeat failure.

## Evidence

- **s03_p04** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes uses heartbeats, too, but not as the primary failure-detection mechanism. Instead, heartbeats have two purposes: polling system load and providing the all-clear signal after a node has been marked as offline. As soon as a heartbeat succeeds, the node is marked as online again. If the heartbeat succeeds despite ongoing server problems (retrieving system load is almost a no-op), …
