---
title: Packfile transfer availability limitation
type: value
id: '6.2'
status: outcome
dimension: '[[concepts/large-repository-object-acquisition|Large-Repository Object Acquisition]]'
accepted_by: []
rejected_by: []
passages: 1
systems: []
tags:
- value
- outcome
- large-repository-object-acquisition
---

# Packfile transfer availability limitation

Packfile-based transfer and filesystem dependence reduce availability when large storage or servers fail.

## Evidence

- **s01_p02** (supports) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
