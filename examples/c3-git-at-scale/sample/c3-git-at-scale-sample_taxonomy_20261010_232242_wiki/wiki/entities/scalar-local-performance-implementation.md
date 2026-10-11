---
title: Scalar-local performance implementation
type: value
id: '11.17'
status: mixed
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s04_p01
- s05_p07
rejected_by:
- s04_p01
- s05_p15
passages: 3
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- mixed
- repository-service-scaling
---

# Scalar-local performance implementation

Performance features are implemented only in the specialized Scalar client rather than upstream Git.

## Evidence

- **s04_p01** (both) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p07** (accepts) · [[sources/s5|Introducing Scalar]] · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
- **s05_p15** (rejects) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
