---
title: Multi-machine repository placement
type: value
id: '1.4'
status: accepted
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by:
- s01_p02
rejected_by: []
passages: 1
systems: []
tags:
- value
- accepted
- repository-replica-placement
---

# Multi-machine repository placement

Place repository data across multiple machines to preserve availability and parallelism.

## Evidence

- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
