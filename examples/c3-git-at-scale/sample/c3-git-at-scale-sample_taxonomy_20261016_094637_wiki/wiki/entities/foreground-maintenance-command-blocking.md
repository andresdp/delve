---
type: Outcome
title: Foreground maintenance command blocking
description: Synchronous garbage collection delays ordinary interactive Git commands.
id: '9.25'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by: []
rejected_by: []
passages: 3
systems:
- /synthesis/systems/goog-dht.md
- /synthesis/systems/ms-scalar.md
tags:
- value
- outcome
- client-repository-performance-strategy
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Foreground maintenance command blocking

Synchronous garbage collection delays ordinary interactive Git commands.

## Evidence

- **s01_p03** (supports) · [Git at any scale](/sources/s1.md) · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
- **s05_p07** (supports) · [Introducing Scalar](/sources/s5.md) · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
- **s05_p09** (supports) · [Introducing Scalar](/sources/s5.md) · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
