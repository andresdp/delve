---
title: Git-aware custom filesystem watcher
type: value
id: '12.12'
status: mixed
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p07
- s05_p15
rejected_by:
- s05_p15
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p020|P020]]'
tags:
- value
- mixed
- client-repository-and-working-tree-scaling
---

# Git-aware custom filesystem watcher

Uses a Git-specific watcher that respects repository exclusions instead of a general-purpose filesystem watcher.

## Evidence

- **s05_p07** (accepts) · [[sources/s5|Introducing Scalar]] · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
- **s05_p15** (both) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## In design points

[[designs/p020|P020]]
