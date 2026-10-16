---
title: Write unavailability during replication shortfall
type: value
id: '30.20'
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

# Write unavailability during replication shortfall

Writes become temporarily unavailable when the required replica count cannot be synchronously achieved.

## Evidence

- **s03_p02** (supports) · [[sources/s3|Building resilience in Spokes]] · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
