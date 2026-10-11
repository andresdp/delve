---
title: Repository hosting reliability objective
type: value
id: '11.20'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s01_p16
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Repository hosting reliability objective

Targets repository availability and dependable service so development and CI continue during failures.

## Evidence

- **s01_p16** (accepts) · [[sources/s1|Git at any scale]] · Origin
  > We are acutely aware of how important it is to host somebody's source code. I think everybody who reads and understands this blog post is just as aware of it. A company can grind to a halt if its developers cannot push or pull from its Git repositories. The productivity cost of five minutes of downtime in your CI system …
