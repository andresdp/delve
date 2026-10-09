---
title: Native Git repository integration
type: value
id: '5.19'
status: accepted
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s01_p06
- s05_p15
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p011|P011]]'
tags:
- value
- accepted
- git-hosting-and-acceleration-integration
---

# Native Git repository integration

Building around Git's native repository format without modifying or forking Git.

## Evidence

- **s01_p06** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## In design points

[[designs/p011|P011]]
