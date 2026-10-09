---
title: Centralized Git hosting architecture
type: value
id: '5.25'
status: accepted
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s01_p01
rejected_by: []
passages: 1
systems: []
design_points:
- '[[designs/p003|P003]]'
- '[[designs/p017|P017]]'
tags:
- value
- accepted
- git-hosting-and-acceleration-integration
---

# Centralized Git hosting architecture

Using a centralized host for repository collaboration despite distributed clients.

## Evidence

- **s01_p01** (accepts) · [[sources/s1|Git at any scale]] · Git at any scale
  > Hosting Git repositories at scale is a nightmare. When Linus Torvalds designed the first version of \*the information manager from hell\* (that's actually the tagline for Git, look it up), he had a very specific use case in mind: his own. He wanted to replace BitKeeper, the distributed version control system that was being used to develop the Linux Kernel. …

## In design points

[[designs/p003|P003]], [[designs/p017|P017]]
