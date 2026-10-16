---
title: Git-level distribution
type: value
id: '22.5'
status: mixed
dimension: '[[concepts/replica-synchronization-mechanism|Replica Synchronization Mechanism]]'
accepted_by:
- s01_p01
- s01_p14
rejected_by:
- s01_p06
passages: 3
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p005|P005]]'
- '[[designs/p012|P012]]'
- '[[designs/p017|P017]]'
- '[[designs/p021|P021]]'
- '[[designs/p022|P022]]'
tags:
- value
- mixed
- replica-synchronization-mechanism
---

# Git-level distribution

The architecture distributes or modifies Git itself to provide repository replication.

## Evidence

- **s01_p01** (accepts) · [[sources/s1|Git at any scale]] · Git at any scale
  > Hosting Git repositories at scale is a nightmare. When Linus Torvalds designed the first version of \*the information manager from hell\* (that's actually the tagline for Git, look it up), he had a very specific use case in mind: his own. He wanted to replace BitKeeper, the distributed version control system that was being used to develop the Linux Kernel. …
- **s01_p06** (rejects) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
- **s01_p14** (accepts) · [[sources/s1|Git at any scale]] · Scale
  > Replication and compaction are the two key factors that determine how well a Git storage system behaves under load. As we’ve just seen, they’re intrinsically linked: the more pushes per second a repository ingests, the more read performance degrades, because the packfiles of every push must be compacted for Git operations to remain efficient. If you replicate these pushes, the …

## In design points

[[designs/p005|P005]], [[designs/p012|P012]], [[designs/p017|P017]], [[designs/p021|P021]], [[designs/p022|P022]]
