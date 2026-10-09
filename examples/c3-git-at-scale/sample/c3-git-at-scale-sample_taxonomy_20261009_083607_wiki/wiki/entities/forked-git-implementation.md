---
title: Forked Git implementation
type: value
id: '5.14'
status: mixed
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s01_p10
rejected_by:
- s01_p06
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p005|P005]]'
tags:
- value
- mixed
- git-hosting-and-acceleration-integration
---

# Forked Git implementation

Maintaining a modified Git implementation for nonstandard repository storage.

## Evidence

- **s01_p06** (rejects) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
- **s01_p10** (accepts) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …

## In design points

[[designs/p005|P005]]
