---
title: Pre-reboot server quiescence
type: value
id: '3.3'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p07
- s03_p08
- s03_p09
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Pre-reboot server quiescence

Allowing existing reads to finish while preventing new reads before reboot or retirement.

## Evidence

- **s03_p07** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > As described above, Spokes can deal quickly and transparently with a server going offline or even failing permanently. So, can we use that for planned maintenance, when we need to reboot or retire a server? Yes and no. Strictly speaking, we can reboot a server with \`sudo reboot\`, and we can retire it just by unplugging it. But there are …
- **s03_p08** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > We don’t perform “chaos monkey” testing on the Spokes file servers, for the same reasons we prefer to quiesce them before rebooting them: to avoid interrupting long-running reads. That is, we do not reboot them randomly just to confirm that sudden, single-node failures are still (mostly) harmless. Instead of “chaos monkey” testing, we perform rolling reboots as needed, which accomplish …
- **s03_p09** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …
