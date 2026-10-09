---
title: Consecutive request-failure quarantine threshold
type: value
id: '3.24'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p03
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Consecutive request-failure quarantine threshold

Quarantining a server after a configured run of consecutive request failures.

## Evidence

- **s03_p03** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes’s availability is a function of the availability of underlying servers and networks, and of our ability to detect and route around server and network problems. Individual servers become unavailable pretty frequently. Since rolling out Spokes this past spring, we have had individual servers crash due to a kernel deadlock and faulty RAM chips. Sometimes servers provide degraded service due …
