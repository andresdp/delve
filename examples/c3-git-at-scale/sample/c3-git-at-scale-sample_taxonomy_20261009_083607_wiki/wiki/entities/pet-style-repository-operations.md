---
title: Pet-style repository operations
type: value
id: '3.31'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s01_p09
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Pet-style repository operations

Each repository copy is individually tracked, monitored, and repaired rather than treated as interchangeable capacity.

## Evidence

- **s01_p09** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
