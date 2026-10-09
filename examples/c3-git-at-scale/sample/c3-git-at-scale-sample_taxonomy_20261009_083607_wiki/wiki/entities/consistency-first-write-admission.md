---
title: Consistency-first write admission
type: value
id: '2.16'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s03_p02
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Consistency-first write admission

Prioritize consistency and partition tolerance over accepting writes during insufficient replication.

## Evidence

- **s03_p02** (accepts) · [[sources/s3|Building resilience in Spokes]] · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
