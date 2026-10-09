---
title: Immediate server reboot
type: value
id: '3.4'
status: mixed
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p09
rejected_by:
- s03_p07
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- mixed
- replica-failure-repair-and-failover
---

# Immediate server reboot

Rebooting immediately without quiescing, potentially interrupting long-running repository reads.

## Evidence

- **s03_p07** (rejects) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > As described above, Spokes can deal quickly and transparently with a server going offline or even failing permanently. So, can we use that for planned maintenance, when we need to reboot or retire a server? Yes and no. Strictly speaking, we can reboot a server with \`sudo reboot\`, and we can retire it just by unplugging it. But there are …
- **s03_p09** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …
