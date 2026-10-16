---
type: Design Alternative
title: Consistency-and-partition-tolerance priority
description: Replica write coordination prioritizes consistency and partition tolerance over write availability.
id: '30.7'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s03_p02
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Consistency-and-partition-tolerance priority

Replica write coordination prioritizes consistency and partition tolerance over write availability.

## Evidence

- **s03_p02** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
