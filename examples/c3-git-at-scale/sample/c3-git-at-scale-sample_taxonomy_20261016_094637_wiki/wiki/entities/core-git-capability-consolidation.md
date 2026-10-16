---
title: Core Git capability consolidation
type: value
id: '9.8'
status: accepted
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s01_p16
- s04_p01
- s05_p02
- s05_p14
rejected_by: []
passages: 4
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-performance-strategy
---

# Core Git capability consolidation

Capabilities formerly supplied by Scalar or management layers are incorporated into core Git, reducing specialized client-layer dependence.

## Evidence

- **s01_p16** (accepts) · [[sources/s1|Git at any scale]] · Origin
  > We are acutely aware of how important it is to host somebody's source code. I think everybody who reads and understands this blog post is just as aware of it. A company can grind to a halt if its developers cannot push or pull from its Git repositories. The productivity cost of five minutes of downtime in your CI system …
- **s04_p01** (accepts) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p02** (accepts) · [[sources/s5|Introducing Scalar]]
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p14** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …
