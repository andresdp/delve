---
title: Synchronous write commitment
type: value
id: '6.3'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s03_p02
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p004|P004]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Synchronous write commitment

A write is accepted only after synchronous commitment establishes the durability promise.

## Evidence

- **s03_p02** (accepts) · [[sources/s3|Building resilience in Spokes]] · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …

## In design points

[[designs/p004|P004]]
