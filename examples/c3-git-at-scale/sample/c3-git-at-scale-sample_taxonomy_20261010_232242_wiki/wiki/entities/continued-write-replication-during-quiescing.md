---
title: Continued write replication during quiescing
type: value
id: '6.20'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s03_p07
- s03_p08
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Continued write replication during quiescing

Continue sending writes to a server draining reads so its replica does not fall arbitrarily behind.

## Evidence

- **s03_p07** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > As described above, Spokes can deal quickly and transparently with a server going offline or even failing permanently. So, can we use that for planned maintenance, when we need to reboot or retire a server? Yes and no. Strictly speaking, we can reboot a server with \`sudo reboot\`, and we can retire it just by unplugging it. But there are …
- **s03_p08** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > We don’t perform “chaos monkey” testing on the Spokes file servers, for the same reasons we prefer to quiesce them before rebooting them: to avoid interrupting long-running reads. That is, we do not reboot them randomly just to confirm that sudden, single-node failures are still (mostly) harmless. Instead of “chaos monkey” testing, we perform rolling reboots as needed, which accomplish …
