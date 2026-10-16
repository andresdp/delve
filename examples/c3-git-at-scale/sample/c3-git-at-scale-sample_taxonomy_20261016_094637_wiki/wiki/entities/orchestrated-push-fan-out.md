---
title: Orchestrated push fan-out
type: value
id: '30.11'
status: accepted
dimension: '[[concepts/replica-write-coordination|Replica Write Coordination]]'
accepted_by:
- s01_p07
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p003|P003]]'
- '[[designs/p020|P020]]'
tags:
- value
- accepted
- replica-write-coordination
---

# Orchestrated push fan-out

An orchestrator distributes pushed packfiles and reference transactions to repository instances.

## Evidence

- **s01_p07** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …

## In design points

[[designs/p003|P003]], [[designs/p020|P020]]
