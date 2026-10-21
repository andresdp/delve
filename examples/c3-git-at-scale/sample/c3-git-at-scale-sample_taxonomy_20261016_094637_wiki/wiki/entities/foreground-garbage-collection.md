---
type: Design Alternative
title: Foreground garbage collection
description: The client periodically performs garbage collection in the foreground during ordinary user work.
id: '9.10'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by: []
rejected_by:
- s05_p09
- s05_p15
passages: 2
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- rejected
- client-repository-performance-strategy
stance: rejected
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Foreground garbage collection

The client periodically performs garbage collection in the foreground during ordinary user work.

## Evidence

- **s05_p09** (rejects) · [Introducing Scalar](/sources/s5.md) · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
- **s05_p15** (rejects) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
