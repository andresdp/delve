---
type: Design Alternative
title: Git-integrated filesystem watching
description: Git uses a watcher that understands repository semantics such as ignore rules to avoid unnecessary scans.
id: '9.6'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p07
- s05_p15
rejected_by: []
passages: 2
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- accepted
- client-repository-performance-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Git-integrated filesystem watching

Git uses a watcher that understands repository semantics such as ignore rules to avoid unnecessary scans.

## Evidence

- **s05_p07** (accepts) · [Introducing Scalar](/sources/s5.md) · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
- **s05_p15** (accepts) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
