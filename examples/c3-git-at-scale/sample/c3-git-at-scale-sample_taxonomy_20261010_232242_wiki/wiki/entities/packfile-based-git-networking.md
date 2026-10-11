---
title: Packfile-based Git networking
type: value
id: '9.12'
status: accepted
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p02
- s01_p06
- s01_p07
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p004|P004]]'
- '[[designs/p019|P019]]'
tags:
- value
- accepted
- repository-storage-representation
---

# Packfile-based Git networking

Uses Git packfiles as the client-server transfer representation regardless of internal server storage.

## Evidence

- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p06** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
- **s01_p07** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …

## In design points

[[designs/p004|P004]], [[designs/p019|P019]]
