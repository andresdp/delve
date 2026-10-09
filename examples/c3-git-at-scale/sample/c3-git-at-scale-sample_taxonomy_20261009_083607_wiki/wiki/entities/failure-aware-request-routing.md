---
title: Failure-aware request routing
type: value
id: '3.28'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p03
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p007|P007]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Failure-aware request routing

Routing repository requests around unavailable or degraded file servers.

## Evidence

- **s03_p03** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes’s availability is a function of the availability of underlying servers and networks, and of our ability to detect and route around server and network problems. Individual servers become unavailable pretty frequently. Since rolling out Spokes this past spring, we have had individual servers crash due to a kernel deadlock and faulty RAM chips. Sometimes servers provide degraded service due …

## In design points

[[designs/p007|P007]]
