---
title: Protection against permanent data loss
type: value
id: '2.38'
status: outcome
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- write-coordination-and-replica-consistency
---

# Protection against permanent data loss

Multiple committed copies make accepted writes highly unlikely to be permanently lost or corrupted.

## Evidence

- **s03_p02** (supports) · [[sources/s3|Building resilience in Spokes]] · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
