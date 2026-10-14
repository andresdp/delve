---
title: Deterministic replica transaction results
type: value
id: '6.25'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s02_p04
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p019|P019]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Deterministic replica transaction results

Replica transaction evaluation produces deterministic reference-update results.

## Evidence

- **s02_p04** (accepts) · [[sources/s2|Stretching Spokes]] · Git reference update transactions
  > Three-phase commit is a core part of keeping the replicas in sync. Implementing it requires each of the replicas to be able to answer the question “can you carry out the following reference updates?”, and then to either commit or roll back the transaction based on the coordinator’s instructions. To make this possible, we implemented transactions for Git reference updates …

## In design points

[[designs/p019|P019]]
