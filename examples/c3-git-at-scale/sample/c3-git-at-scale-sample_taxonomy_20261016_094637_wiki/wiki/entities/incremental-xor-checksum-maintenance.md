---
type: Design Alternative
title: Incremental XOR checksum maintenance
description: Reference changes update the logical-state checksum incrementally by removing the old pair hash and adding the new one.
id: '27.2'
dimension: /concepts/replica-state-comparison.md
accepted_by:
- s02_p05
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p011.md
- /designs/p014.md
- /designs/p015.md
tags:
- value
- accepted
- replica-state-comparison
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Incremental XOR checksum maintenance

Reference changes update the logical-state checksum incrementally by removing the old pair hash and adding the new one.

## Evidence

- **s02_p05** (accepts) · [Stretching Spokes](/sources/s2.md) · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …

## In design points

[P011](/designs/p011.md), [P014](/designs/p014.md), [P015](/designs/p015.md)
