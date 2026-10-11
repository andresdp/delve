---
title: Push unavailability without quorum
type: value
id: '6.38'
status: outcome
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- write-commitment-and-consistency
---

# Push unavailability without quorum

Corruption or loss of sufficient healthy copies prevents accepting new pushes.

## Evidence

- **s01_p09** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
