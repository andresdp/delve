---
type: Design Alternative
title: Full checksum recomputation
description: Replica consistency checks recompute the checksum from all references for every update.
id: '27.3'
dimension: /concepts/replica-state-comparison.md
accepted_by:
- s01_p09
- s02_p05
rejected_by:
- s02_p05
passages: 2
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p006.md
- /designs/p018.md
tags:
- value
- mixed
- replica-state-comparison
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Full checksum recomputation

Replica consistency checks recompute the checksum from all references for every update.

## Evidence

- **s01_p09** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s02_p05** (both) · [Stretching Spokes](/sources/s2.md) · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …

## In design points

[P006](/designs/p006.md), [P018](/designs/p018.md)
