---
title: Supplemental heartbeat recovery signals
type: value
id: '3.15'
status: mixed
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p04
rejected_by:
- s03_p03
- s03_p04
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- mixed
- replica-failure-repair-and-failover
---

# Supplemental heartbeat recovery signals

Use heartbeats for load polling and recovery marking without making them primary failure detectors.

## Evidence

- **s03_p03** (rejects) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes’s availability is a function of the availability of underlying servers and networks, and of our ability to detect and route around server and network problems. Individual servers become unavailable pretty frequently. Since rolling out Spokes this past spring, we have had individual servers crash due to a kernel deadlock and faulty RAM chips. Sometimes servers provide degraded service due …
- **s03_p04** (both) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes uses heartbeats, too, but not as the primary failure-detection mechanism. Instead, heartbeats have two purposes: polling system load and providing the all-clear signal after a node has been marked as offline. As soon as a heartbeat succeeds, the node is marked as online again. If the heartbeat succeeds despite ongoing server problems (retrieving system load is almost a no-op), …
