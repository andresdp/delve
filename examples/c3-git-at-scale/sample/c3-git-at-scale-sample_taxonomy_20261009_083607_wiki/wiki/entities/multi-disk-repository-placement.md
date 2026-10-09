---
title: Multi-disk repository placement
type: value
id: '1.3'
status: accepted
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by:
- s01_p02
rejected_by: []
passages: 1
systems: []
design_points:
- '[[designs/p010|P010]]'
tags:
- value
- accepted
- repository-replica-placement
---

# Multi-disk repository placement

Distribute one repository across multiple disks to increase parallel operation capacity.

## Evidence

- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …

## In design points

[[designs/p010|P010]]
