---
title: Client-compatible clone efficiency
type: value
id: '4.34'
status: outcome
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- client-repository-workload-scaling
---

# Client-compatible clone efficiency

Preserving efficient Git-client cloning by retaining native repository data.

## Evidence

- **s01_p06** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
