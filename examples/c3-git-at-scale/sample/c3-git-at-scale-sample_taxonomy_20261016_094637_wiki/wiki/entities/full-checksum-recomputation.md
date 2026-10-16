---
title: Full checksum recomputation
type: value
id: '27.3'
status: mixed
dimension: '[[concepts/replica-state-comparison|Replica State Comparison]]'
accepted_by:
- s01_p09
- s02_p05
rejected_by:
- s02_p05
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p006|P006]]'
- '[[designs/p018|P018]]'
tags:
- value
- mixed
- replica-state-comparison
---

# Full checksum recomputation

Replica consistency checks recompute the checksum from all references for every update.

## Evidence

- **s01_p09** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s02_p05** (both) · [[sources/s2|Stretching Spokes]] · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …

## In design points

[[designs/p006|P006]], [[designs/p018|P018]]
