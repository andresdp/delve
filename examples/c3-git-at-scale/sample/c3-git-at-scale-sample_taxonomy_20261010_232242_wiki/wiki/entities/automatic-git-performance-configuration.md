---
title: Automatic Git performance configuration
type: value
id: '11.15'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s04_p01
- s05_p01
- s05_p02
- s05_p07
- s05_p15
rejected_by: []
passages: 5
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Automatic Git performance configuration

Repository registration applies recommended local Git settings automatically.

## Evidence

- **s04_p01** (accepts) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p01** (accepts) · [[sources/s5|Introducing Scalar]]
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p02** (accepts) · [[sources/s5|Introducing Scalar]]
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p07** (accepts) · [[sources/s5|Introducing Scalar]] · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
