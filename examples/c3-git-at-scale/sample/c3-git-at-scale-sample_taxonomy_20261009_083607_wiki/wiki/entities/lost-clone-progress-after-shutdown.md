---
title: Lost clone progress after shutdown
type: value
id: '3.33'
status: outcome
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-failure-repair-and-failover
---

# Lost clone progress after shutdown

Resulting user impact when an abrupt shutdown interrupts a large clone and forces it to restart elsewhere.

## Evidence

- **s03_p07** (supports) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > As described above, Spokes can deal quickly and transparently with a server going offline or even failing permanently. So, can we use that for planned maintenance, when we need to reboot or retire a server? Yes and no. Strictly speaking, we can reboot a server with \`sudo reboot\`, and we can retire it just by unplugging it. But there are …
