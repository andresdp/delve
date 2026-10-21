---
type: Design Alternative
title: Virtualized filesystem client
description: A virtualized filesystem defers populated-size costs to improve large-repository client performance.
id: '9.9'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p01
rejected_by:
- s05_p15
passages: 2
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- mixed
- client-repository-performance-strategy
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Virtualized filesystem client

A virtualized filesystem defers populated-size costs to improve large-repository client performance.

## Evidence

- **s05_p01** (accepts) · [Introducing Scalar](/sources/s5.md)
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p15** (rejects) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
