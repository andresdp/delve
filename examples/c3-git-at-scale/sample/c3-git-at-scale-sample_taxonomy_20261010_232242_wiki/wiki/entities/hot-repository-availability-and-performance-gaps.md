---
title: Hot-repository availability and performance gaps
type: value
id: '11.51'
status: outcome
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- outcome
- repository-service-scaling
---

# Hot-repository availability and performance gaps

Leaves busy repositories exposed to single-machine availability limits and concentrated performance bottlenecks.

## Evidence

- **s01_p05** (supports) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
