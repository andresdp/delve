---
title: HTTP daemon over on-disk repository
type: value
id: '1.5'
status: rejected
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by: []
rejected_by:
- s01_p02
passages: 1
systems: []
design_points:
- '[[designs/p015|P015]]'
tags:
- value
- rejected
- repository-replica-placement
---

# HTTP daemon over on-disk repository

Place an HTTP daemon directly in front of a filesystem-resident repository.

## Evidence

- **s01_p02** (rejects) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …

## In design points

[[designs/p015|P015]]
