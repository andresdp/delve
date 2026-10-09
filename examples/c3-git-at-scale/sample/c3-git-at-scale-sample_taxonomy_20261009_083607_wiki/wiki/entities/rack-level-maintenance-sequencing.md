---
title: Rack-level maintenance sequencing
type: value
id: '3.5'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p08
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Rack-level maintenance sequencing

Treating racks as availability zones and completing maintenance on one rack before proceeding to another.

## Evidence

- **s03_p08** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > We don’t perform “chaos monkey” testing on the Spokes file servers, for the same reasons we prefer to quiesce them before rebooting them: to avoid interrupting long-running reads. That is, we do not reboot them randomly just to confirm that sudden, single-node failures are still (mostly) harmless. Instead of “chaos monkey” testing, we perform rolling reboots as needed, which accomplish …
