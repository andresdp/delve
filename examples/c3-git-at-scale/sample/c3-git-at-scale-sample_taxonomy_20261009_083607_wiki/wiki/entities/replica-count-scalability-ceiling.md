---
title: Replica-count scalability ceiling
type: value
id: '1.14'
status: outcome
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- repository-replica-placement
---

# Replica-count scalability ceiling

Adding replicas to a synchronous transaction cluster produces tail latency and limits repository push throughput.

## Evidence

- **s01_p08** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
