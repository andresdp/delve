---
title: Core Git upstreaming
type: value
id: '11.13'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s04_p01
- s05_p02
- s05_p14
- s05_p15
rejected_by: []
passages: 4
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p015|P015]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Core Git upstreaming

Performance capabilities are implemented in and contributed to core Git so specialized-client dependencies can eventually be removed.

## Evidence

- **s04_p01** (accepts) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p02** (accepts) · [[sources/s5|Introducing Scalar]]
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p14** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## In design points

[[designs/p015|P015]]
