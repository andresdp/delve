---
title: External repository-machine routing database
type: value
id: '3.30'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s01_p09
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p006|P006]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# External repository-machine routing database

A maintained routing table maps each repository to every machine hosting a replica.

## Evidence

- **s01_p09** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …

## In design points

[[designs/p006|P006]]
