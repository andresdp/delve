---
title: Application layer over unmodified Git
type: value
id: '9.16'
status: accepted
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p007|P007]]'
tags:
- value
- accepted
- repository-storage-representation
---

# Application layer over unmodified Git

Hosting features are built above standard Git repositories without maintaining a Git fork.

## Evidence

- **s01_p06** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …

## In design points

[[designs/p007|P007]]
