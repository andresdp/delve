---
title: Explicit repository-location tracking
type: value
id: '13.2'
status: accepted
dimension: '[[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]]'
accepted_by:
- s01_p09
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p005|P005]]'
- '[[designs/p006|P006]]'
tags:
- value
- accepted
- repository-placement-and-read-routing
---

# Explicit repository-location tracking

An external routing table records the machines holding each repository copy and supports locating and validating those copies.

## Evidence

- **s01_p09** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …

## In design points

[[designs/p005|P005]], [[designs/p006|P006]]
