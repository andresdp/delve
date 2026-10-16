---
type: Design Alternative
title: Native Git scalability improvements
description: Large-repository performance is improved in Git itself through features such as commit graphs and sparse-checkout enhancements.
id: '9.2'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s01_p10
- s04_p01
- s05_p01
- s05_p02
- s05_p10
- s05_p14
rejected_by: []
passages: 6
systems:
- /synthesis/systems/cur-cont.md
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

# Native Git scalability improvements

Large-repository performance is improved in Git itself through features such as commit graphs and sparse-checkout enhancements.

## Evidence

- **s01_p10** (accepts) · [Git at any scale](/sources/s1.md) · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
- **s04_p01** (accepts) · [Scalar philosophy](/sources/s4.md)
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p01** (accepts) · [Introducing Scalar](/sources/s5.md)
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p02** (accepts) · [Introducing Scalar](/sources/s5.md)
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p10** (accepts) · [Introducing Scalar](/sources/s5.md) · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
- **s05_p14** (accepts) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …
