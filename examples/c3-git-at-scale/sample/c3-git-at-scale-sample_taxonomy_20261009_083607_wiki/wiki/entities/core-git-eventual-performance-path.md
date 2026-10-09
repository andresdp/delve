---
title: Core Git eventual performance path
type: value
id: '5.17'
status: accepted
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s04_p01
- s05_p14
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p020|P020]]'
tags:
- value
- accepted
- git-hosting-and-acceleration-integration
---

# Core Git eventual performance path

Transitioning performance capabilities from Scalar into the core Git client.

## Evidence

- **s04_p01** (accepts) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p14** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …

## In design points

[[designs/p020|P020]]
