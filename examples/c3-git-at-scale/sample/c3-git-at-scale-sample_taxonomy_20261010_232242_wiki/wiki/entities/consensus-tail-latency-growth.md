---
title: Consensus tail-latency growth
type: value
id: '6.32'
status: outcome
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- write-commitment-and-consistency
---

# Consensus tail-latency growth

Adding replicas increases the influence of the slowest participant on three-phase-commit latency.

## Evidence

- **s01_p08** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
