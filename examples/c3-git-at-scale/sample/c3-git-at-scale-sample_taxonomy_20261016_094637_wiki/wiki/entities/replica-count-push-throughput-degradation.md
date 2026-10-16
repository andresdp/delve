---
title: Replica-count push-throughput degradation
type: value
id: '30.18'
status: outcome
dimension: '[[concepts/replica-write-coordination|Replica Write Coordination]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-write-coordination
---

# Replica-count push-throughput degradation

Adding replicas reduces push throughput because consensus waits on more participants and their tail latency.

## Evidence

- **s01_p08** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
