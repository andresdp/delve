---
type: Design Alternative
title: Core Git capability consolidation
description: Capabilities formerly supplied by Scalar or management layers are incorporated into core Git, reducing specialized client-layer dependence.
id: '9.8'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s01_p16
- s04_p01
- s05_p02
- s05_p14
rejected_by: []
passages: 4
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

# Core Git capability consolidation

Capabilities formerly supplied by Scalar or management layers are incorporated into core Git, reducing specialized client-layer dependence.

## Evidence

- **s01_p16** (accepts) · [Git at any scale](/sources/s1.md) · Origin
  > We are acutely aware of how important it is to host somebody's source code. I think everybody who reads and understands this blog post is just as aware of it. A company can grind to a halt if its developers cannot push or pull from its Git repositories. The productivity cost of five minutes of downtime in your CI system …
- **s04_p01** (accepts) · [Scalar philosophy](/sources/s4.md)
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p02** (accepts) · [Introducing Scalar](/sources/s5.md)
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p14** (accepts) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …
