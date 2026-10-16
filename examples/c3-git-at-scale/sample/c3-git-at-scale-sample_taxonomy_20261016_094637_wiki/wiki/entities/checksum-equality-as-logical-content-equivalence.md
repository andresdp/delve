---
type: Outcome
title: Checksum equality as logical-content equivalence
description: Equal replica checksums indicate equivalent logical repository contents.
id: '27.4'
dimension: /concepts/replica-state-comparison.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- outcome
- replica-state-comparison
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Checksum equality as logical-content equivalence

Equal replica checksums indicate equivalent logical repository contents.

## Evidence

- **s02_p05** (supports) · [Stretching Spokes](/sources/s2.md) · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …
