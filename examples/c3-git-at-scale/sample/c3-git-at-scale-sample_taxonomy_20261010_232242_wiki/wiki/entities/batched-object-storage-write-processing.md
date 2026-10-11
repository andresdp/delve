---
title: Batched object-storage write processing
type: value
id: '11.42'
status: mixed
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s01_p01
- s01_p10
rejected_by:
- s01_p10
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
merged_from:
- id: '11.64'
  label: Single object-storage write per push
tags:
- value
- mixed
- repository-service-scaling
---

# Batched object-storage write processing

Batching durable object-storage writes rather than imposing independent object-store latency on every push.

## Evidence

- **s01_p01** (accepts) · [[sources/s1|Git at any scale]] · Git at any scale
  > Hosting Git repositories at scale is a nightmare. When Linus Torvalds designed the first version of \*the information manager from hell\* (that's actually the tagline for Git, look it up), he had a very specific use case in mind: his own. He wanted to replace BitKeeper, the distributed version control system that was being used to develop the Linux Kernel. …
- **s01_p10** (both) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …

## Merged from

- {'id': '11.64', 'label': 'Single object-storage write per push'}
