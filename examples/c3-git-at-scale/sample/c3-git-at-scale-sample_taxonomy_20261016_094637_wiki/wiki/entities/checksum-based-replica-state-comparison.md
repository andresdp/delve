---
title: Checksum-based replica state comparison
type: value
id: '27.1'
status: accepted
dimension: '[[concepts/replica-state-comparison|Replica State Comparison]]'
accepted_by:
- s02_p05
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p002|P002]]'
- '[[designs/p004|P004]]'
- '[[designs/p005|P005]]'
- '[[designs/p019|P019]]'
tags:
- value
- accepted
- replica-state-comparison
---

# Checksum-based replica state comparison

A checksum summarizes logical replica state for equality checking after updates.

## Evidence

- **s02_p05** (accepts) · [[sources/s2|Stretching Spokes]] · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …

## In design points

[[designs/p002|P002]], [[designs/p004|P004]], [[designs/p005|P005]], [[designs/p019|P019]]
