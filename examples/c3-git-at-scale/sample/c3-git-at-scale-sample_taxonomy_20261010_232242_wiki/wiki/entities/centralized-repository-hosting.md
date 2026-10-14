---
title: Centralized repository hosting
type: value
id: '9.1'
status: accepted
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p01
- s01_p04
- s01_p16
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
design_points:
- '[[designs/p005|P005]]'
- '[[designs/p010|P010]]'
- '[[designs/p024|P024]]'
tags:
- value
- accepted
- repository-storage-representation
---

# Centralized repository hosting

A centralized service provides the primary repository access point despite Git's distributed capabilities.

## Evidence

- **s01_p01** (accepts) · [[sources/s1|Git at any scale]] · Git at any scale
  > Hosting Git repositories at scale is a nightmare. When Linus Torvalds designed the first version of \*the information manager from hell\* (that's actually the tagline for Git, look it up), he had a very specific use case in mind: his own. He wanted to replace BitKeeper, the distributed version control system that was being used to develop the Linux Kernel. …
- **s01_p04** (accepts) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > A couple years after Git started to escape its Linux Kernel bubble, a scrappy startup was born in San Francisco. GitHub was founded in 2008 as a social coding platform with a very prescient tagline, "Git repository hosting: no longer a pain in the ass." I'm not joking here either, look it up. There was, all the way back in …
- **s01_p16** (accepts) · [[sources/s1|Git at any scale]] · Origin
  > We are acutely aware of how important it is to host somebody's source code. I think everybody who reads and understands this blog post is just as aware of it. A company can grind to a halt if its developers cannot push or pull from its Git repositories. The productivity cost of five minutes of downtime in your CI system …

## In design points

[[designs/p005|P005]], [[designs/p010|P010]], [[designs/p024|P024]]
