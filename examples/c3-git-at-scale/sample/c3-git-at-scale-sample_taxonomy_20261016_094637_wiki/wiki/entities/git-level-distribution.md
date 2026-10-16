---
type: Design Alternative
title: Git-level distribution
description: The architecture distributes or modifies Git itself to provide repository replication.
id: '22.5'
dimension: /concepts/replica-synchronization-mechanism.md
accepted_by:
- s01_p01
- s01_p14
rejected_by:
- s01_p06
passages: 3
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p005.md
- /designs/p012.md
- /designs/p017.md
- /designs/p021.md
- /designs/p022.md
tags:
- value
- mixed
- replica-synchronization-mechanism
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Git-level distribution

The architecture distributes or modifies Git itself to provide repository replication.

## Evidence

- **s01_p01** (accepts) · [Git at any scale](/sources/s1.md) · Git at any scale
  > Hosting Git repositories at scale is a nightmare. When Linus Torvalds designed the first version of \*the information manager from hell\* (that's actually the tagline for Git, look it up), he had a very specific use case in mind: his own. He wanted to replace BitKeeper, the distributed version control system that was being used to develop the Linux Kernel. …
- **s01_p06** (rejects) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
- **s01_p14** (accepts) · [Git at any scale](/sources/s1.md) · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …

## In design points

[P005](/designs/p005.md), [P012](/designs/p012.md), [P017](/designs/p017.md), [P021](/designs/p021.md), [P022](/designs/p022.md)
