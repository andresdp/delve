---
type: Outcome
title: Replica-count push-throughput degradation
description: Adding replicas reduces push throughput because consensus waits on more participants and their tail latency.
id: '30.18'
dimension: /concepts/replica-write-coordination.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- outcome
- replica-write-coordination
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica-count push-throughput degradation

Adding replicas reduces push throughput because consensus waits on more participants and their tail latency.

## Evidence

- **s01_p08** (supports) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
