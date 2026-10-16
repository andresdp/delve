---
title: Incremental XOR checksum maintenance
type: value
id: '27.2'
status: accepted
dimension: '[[concepts/replica-state-comparison|Replica State Comparison]]'
accepted_by:
- s02_p05
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p011|P011]]'
- '[[designs/p014|P014]]'
- '[[designs/p015|P015]]'
tags:
- value
- accepted
- replica-state-comparison
---

# Incremental XOR checksum maintenance

Reference changes update the logical-state checksum incrementally by removing the old pair hash and adding the new one.

## Evidence

- **s02_p05** (accepts) · [[sources/s2|Stretching Spokes]] · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …

## In design points

[[designs/p011|P011]], [[designs/p014|P014]], [[designs/p015|P015]]
