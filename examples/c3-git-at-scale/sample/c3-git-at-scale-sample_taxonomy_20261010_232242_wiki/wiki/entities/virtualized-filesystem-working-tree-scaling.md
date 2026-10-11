---
title: Virtualized filesystem working-tree scaling
type: value
id: '12.14'
status: mixed
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p01
rejected_by:
- s05_p15
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
merged_from:
- id: '12.42'
  label: Virtualized filesystem working-tree scaling
tags:
- value
- mixed
- client-repository-and-working-tree-scaling
---

# Virtualized filesystem working-tree scaling

Uses a virtualized filesystem to defer populated working-tree costs and accelerate checkout presentation.

## Evidence

- **s05_p01** (accepts) · [[sources/s5|Introducing Scalar]]
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p15** (rejects) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## Merged from

- {'id': '12.42', 'label': 'Virtualized filesystem working-tree scaling'}
