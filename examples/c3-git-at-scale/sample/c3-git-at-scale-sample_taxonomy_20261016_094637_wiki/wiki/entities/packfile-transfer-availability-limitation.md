---
type: Outcome
title: Packfile transfer availability limitation
description: Packfile-based transfer and filesystem dependence reduce availability when large storage or servers fail.
id: '6.2'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by: []
rejected_by: []
passages: 1
systems: []
tags:
- value
- outcome
- large-repository-object-acquisition
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Packfile transfer availability limitation

Packfile-based transfer and filesystem dependence reduce availability when large storage or servers fail.

## Evidence

- **s01_p02** (supports) · [Git at any scale](/sources/s1.md) · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
