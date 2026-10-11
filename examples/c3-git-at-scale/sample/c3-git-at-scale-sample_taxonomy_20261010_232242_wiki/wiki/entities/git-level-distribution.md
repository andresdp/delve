---
title: Git-level distribution
type: value
id: '9.14'
status: mixed
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p02
rejected_by:
- s01_p06
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p014|P014]]'
tags:
- value
- mixed
- repository-storage-representation
---

# Git-level distribution

Repository distribution modifies or distributes Git itself rather than replicating repository data above it.

## Evidence

- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p06** (rejects) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …

## In design points

[[designs/p014|P014]]
