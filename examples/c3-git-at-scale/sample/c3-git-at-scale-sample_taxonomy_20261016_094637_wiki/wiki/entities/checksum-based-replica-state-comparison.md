---
type: Design Alternative
title: Checksum-based replica state comparison
description: A checksum summarizes logical replica state for equality checking after updates.
id: '27.1'
dimension: /concepts/replica-state-comparison.md
accepted_by:
- s02_p05
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p002.md
- /designs/p004.md
- /designs/p005.md
- /designs/p019.md
tags:
- value
- accepted
- replica-state-comparison
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Checksum-based replica state comparison

A checksum summarizes logical replica state for equality checking after updates.

## Evidence

- **s02_p05** (accepts) · [Stretching Spokes](/sources/s2.md) · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …

## In design points

[P002](/designs/p002.md), [P004](/designs/p004.md), [P005](/designs/p005.md), [P019](/designs/p019.md)
