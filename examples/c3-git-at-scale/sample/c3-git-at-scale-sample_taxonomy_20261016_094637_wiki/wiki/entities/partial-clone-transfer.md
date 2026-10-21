---
type: Design Alternative
title: Partial clone transfer
description: Clients use partial clone to reduce large-repository transfer time and local storage when the hosting service supports it.
id: '6.7'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by:
- s04_p01
- s04_p02
- s05_p08
rejected_by: []
passages: 3
systems:
- /synthesis/systems/ms-gvfs.md
- /synthesis/systems/ms-scalar.md
design_points:
- /designs/p013.md
- /designs/p018.md
tags:
- value
- accepted
- large-repository-object-acquisition
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Partial clone transfer

Clients use partial clone to reduce large-repository transfer time and local storage when the hosting service supports it.

## Evidence

- **s04_p01** (accepts) · [Scalar philosophy](/sources/s4.md)
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s04_p02** (accepts) · [Scalar philosophy](/sources/s4.md)
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p08** (accepts) · [Introducing Scalar](/sources/s5.md) · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …

## In design points

[P013](/designs/p013.md), [P018](/designs/p018.md)
