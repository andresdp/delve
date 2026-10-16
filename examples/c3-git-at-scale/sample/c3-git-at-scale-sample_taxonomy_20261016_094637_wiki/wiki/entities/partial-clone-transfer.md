---
title: Partial clone transfer
type: value
id: '6.7'
status: accepted
dimension: '[[concepts/large-repository-object-acquisition|Large-Repository Object Acquisition]]'
accepted_by:
- s04_p01
- s04_p02
- s05_p08
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p013|P013]]'
- '[[designs/p018|P018]]'
tags:
- value
- accepted
- large-repository-object-acquisition
---

# Partial clone transfer

Clients use partial clone to reduce large-repository transfer time and local storage when the hosting service supports it.

## Evidence

- **s04_p01** (accepts) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s04_p02** (accepts) · [[sources/s4|Scalar philosophy]]
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p08** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …

## In design points

[[designs/p013|P013]], [[designs/p018|P018]]
