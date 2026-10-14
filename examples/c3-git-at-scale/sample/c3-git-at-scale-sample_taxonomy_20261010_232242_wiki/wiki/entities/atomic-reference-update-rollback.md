---
title: Atomic reference-update rollback
type: value
id: '6.28'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s01_p07
- s02_p04
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p009|P009]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Atomic reference-update rollback

Failed tentative reference transactions are rolled back in full.

## Evidence

- **s01_p07** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s02_p04** (accepts) · [[sources/s2|Stretching Spokes]] · Git reference update transactions
  > Three-phase commit is a core part of keeping the replicas in sync. Implementing it requires each of the replicas to be able to answer the question “can you carry out the following reference updates?”, and then to either commit or roll back the transaction based on the coordinator’s instructions. To make this possible, we implemented transactions for Git reference updates …

## In design points

[[designs/p009|P009]]
