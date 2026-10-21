---
type: Design Alternative
title: Explicit repository-location tracking
description: An external routing table records the machines holding each repository copy and supports locating and validating those copies.
id: '13.2'
dimension: /concepts/repository-placement-and-read-routing.md
accepted_by:
- s01_p09
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p005.md
- /designs/p006.md
tags:
- value
- accepted
- repository-placement-and-read-routing
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Explicit repository-location tracking

An external routing table records the machines holding each repository copy and supports locating and validating those copies.

## Evidence

- **s01_p09** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …

## In design points

[P005](/designs/p005.md), [P006](/designs/p006.md)
