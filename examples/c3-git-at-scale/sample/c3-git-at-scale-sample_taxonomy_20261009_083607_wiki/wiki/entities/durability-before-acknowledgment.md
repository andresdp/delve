---
title: Durability-before-acknowledgment
type: value
id: '2.2'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s01_p10
- s03_p02
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p012|P012]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Durability-before-acknowledgment

Acknowledging a push only after its write-ahead-log entry is fully persisted.

## Evidence

- **s01_p10** (accepts) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
- **s03_p02** (accepts) · [[sources/s3|Building resilience in Spokes]] · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …

## In design points

[[designs/p012|P012]]
