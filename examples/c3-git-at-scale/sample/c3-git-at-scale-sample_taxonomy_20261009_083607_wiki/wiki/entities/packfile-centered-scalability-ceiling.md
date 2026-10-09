---
title: Packfile-centered scalability ceiling
type: value
id: '1.13'
status: outcome
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by: []
rejected_by: []
passages: 1
systems: []
tags:
- value
- outcome
- repository-replica-placement
---

# Packfile-centered scalability ceiling

Filesystem-dependent packfiles limit repository scalability, availability, and parallel operation capacity.

## Evidence

- **s01_p02** (supports) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
