---
title: Heartbeat-based primary failure detection
type: value
id: '3.16'
status: rejected
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by: []
rejected_by:
- s03_p03
- s03_p04
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- rejected
- replica-failure-repair-and-failover
---

# Heartbeat-based primary failure detection

Use heartbeat failure as the primary test for replica unavailability.

## Evidence

- **s03_p03** (rejects) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes’s availability is a function of the availability of underlying servers and networks, and of our ability to detect and route around server and network problems. Individual servers become unavailable pretty frequently. Since rolling out Spokes this past spring, we have had individual servers crash due to a kernel deadlock and faulty RAM chips. Sometimes servers provide degraded service due …
- **s03_p04** (rejects) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes uses heartbeats, too, but not as the primary failure-detection mechanism. Instead, heartbeats have two purposes: polling system load and providing the all-clear signal after a node has been marked as offline. As soon as a heartbeat succeeds, the node is marked as online again. If the heartbeat succeeds despite ongoing server problems (retrieving system load is almost a no-op), …
