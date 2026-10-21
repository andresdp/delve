---
type: Design Alternative
title: Standard-Git GVFS protocol support
description: The GVFS protocol is not incorporated into the standard Git client.
id: '6.8'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by:
- s04_p01
- s05_p01
- s05_p03
- s05_p08
- s05_p15
rejected_by:
- s04_p01
passages: 5
systems:
- /synthesis/systems/ms-gvfs.md
- /synthesis/systems/ms-scalar.md
design_points:
- /designs/p003.md
- /designs/p017.md
tags:
- value
- mixed
- large-repository-object-acquisition
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Standard-Git GVFS protocol support

The GVFS protocol is not incorporated into the standard Git client.

## Evidence

- **s04_p01** (both) · [Scalar philosophy](/sources/s4.md)
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p01** (accepts) · [Introducing Scalar](/sources/s5.md)
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p03** (accepts) · [Introducing Scalar](/sources/s5.md) · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p08** (accepts) · [Introducing Scalar](/sources/s5.md) · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
- **s05_p15** (accepts) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## In design points

[P003](/designs/p003.md), [P017](/designs/p017.md)
