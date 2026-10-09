---
title: Eventually consistent repository views
type: value
id: '2.26'
status: rejected
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by: []
rejected_by:
- s01_p06
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- rejected
- write-coordination-and-replica-consistency
---

# Eventually consistent repository views

Allowing replicas to expose temporarily divergent repository state.

## Evidence

- **s01_p06** (rejects) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
