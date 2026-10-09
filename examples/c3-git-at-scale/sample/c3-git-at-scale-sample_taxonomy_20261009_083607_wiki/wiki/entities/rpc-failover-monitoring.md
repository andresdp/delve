---
title: RPC failover monitoring
type: value
id: '3.21'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p04
- s03_p05
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# RPC failover monitoring

Use redirected operation patterns to detect misbehaving repository servers.

## Evidence

- **s03_p04** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes uses heartbeats, too, but not as the primary failure-detection mechanism. Instead, heartbeats have two purposes: polling system load and providing the all-clear signal after a node has been marked as offline. As soon as a heartbeat succeeds, the node is marked as online again. If the heartbeat succeeds despite ongoing server problems (retrieving system load is almost a no-op), …
- **s03_p05** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …
