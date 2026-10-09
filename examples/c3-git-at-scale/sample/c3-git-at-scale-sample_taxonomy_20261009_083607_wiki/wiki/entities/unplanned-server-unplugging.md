---
title: Unplanned server unplugging
type: value
id: '3.9'
status: rejected
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by: []
rejected_by:
- s03_p08
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- rejected
- replica-failure-repair-and-failover
---

# Unplanned server unplugging

Removing a server abruptly without controlled quiescence or failure-handling procedures.

## Evidence

- **s03_p08** (rejects) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > We don’t perform “chaos monkey” testing on the Spokes file servers, for the same reasons we prefer to quiesce them before rebooting them: to avoid interrupting long-running reads. That is, we do not reboot them randomly just to confirm that sudden, single-node failures are still (mostly) harmless. Instead of “chaos monkey” testing, we perform rolling reboots as needed, which accomplish …
