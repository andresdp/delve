---
type: Design Alternative
title: Integrated client optimization configuration
description: A managed client setup combines configuration, metadata acceleration, filesystem monitoring, fetching, and background maintenance for large repositories.
id: '9.1'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s04_p01
- s04_p02
- s05_p02
- s05_p10
rejected_by: []
passages: 4
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

# Integrated client optimization configuration

A managed client setup combines configuration, metadata acceleration, filesystem monitoring, fetching, and background maintenance for large repositories.

## Evidence

- **s04_p01** (accepts) · [Scalar philosophy](/sources/s4.md)
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s04_p02** (accepts) · [Scalar philosophy](/sources/s4.md)
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p02** (accepts) · [Introducing Scalar](/sources/s5.md)
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p10** (accepts) · [Introducing Scalar](/sources/s5.md) · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
