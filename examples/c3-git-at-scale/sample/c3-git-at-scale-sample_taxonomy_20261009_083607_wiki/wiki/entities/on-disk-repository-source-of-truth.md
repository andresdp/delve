---
title: On-disk repository source of truth
type: value
id: '1.10'
status: accepted
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by:
- s01_p09
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- repository-replica-placement
---

# On-disk repository source of truth

Authoritative repository state is maintained in replicated on-disk repository copies.

## Evidence

- **s01_p09** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
