---
title: Packfile-level replication
type: value
id: '2.27'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s01_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Packfile-level replication

Replicating Git data at the packfile layer rather than distributing Git itself.

## Evidence

- **s01_p06** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
