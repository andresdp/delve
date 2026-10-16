---
title: Checksum equality as logical-content equivalence
type: value
id: '27.4'
status: outcome
dimension: '[[concepts/replica-state-comparison|Replica State Comparison]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-state-comparison
---

# Checksum equality as logical-content equivalence

Equal replica checksums indicate equivalent logical repository contents.

## Evidence

- **s02_p05** (supports) · [[sources/s2|Stretching Spokes]] · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …
