---
title: Partial clone
type: value
id: '4.5'
status: accepted
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s04_p01
- s04_p02
- s05_p15
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p017|P017]]'
tags:
- value
- accepted
- client-repository-workload-scaling
---

# Partial clone

Downloading only objects needed for the current checkout to reduce client transfer and storage.

## Evidence

- **s04_p01** (accepts) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s04_p02** (accepts) · [[sources/s4|Scalar philosophy]]
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## In design points

[[designs/p017|P017]]
