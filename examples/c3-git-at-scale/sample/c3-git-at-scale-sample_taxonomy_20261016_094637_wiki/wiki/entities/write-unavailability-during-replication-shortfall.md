---
type: Outcome
title: Write unavailability during replication shortfall
description: Writes become temporarily unavailable when the required replica count cannot be synchronously achieved.
id: '30.20'
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

# Write unavailability during replication shortfall

Writes become temporarily unavailable when the required replica count cannot be synchronously achieved.

## Evidence

- **s03_p02** (supports) · [Building resilience in Spokes](/sources/s3.md) · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
