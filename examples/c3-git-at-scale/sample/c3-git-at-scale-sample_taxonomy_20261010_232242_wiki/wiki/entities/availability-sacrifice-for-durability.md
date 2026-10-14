---
title: Availability sacrifice for durability
type: value
id: '6.37'
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

# Availability sacrifice for durability

Temporary write unavailability results from refusing writes that cannot be safely replicated.

## Evidence

- **s03_p02** (supports) · [[sources/s3|Building resilience in Spokes]] · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
