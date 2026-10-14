---
title: Filesystem-level repository distribution
type: value
id: '9.3'
status: accepted
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p02
- s01_p04
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
design_points:
- '[[designs/p002|P002]]'
tags:
- value
- accepted
- repository-storage-representation
---

# Filesystem-level repository distribution

Repositories are distributed through the filesystem layer to scale application instances without changing Rails or Git internals.

## Evidence

- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p04** (accepts) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > A couple years after Git started to escape its Linux Kernel bubble, a scrappy startup was born in San Francisco. GitHub was founded in 2008 as a social coding platform with a very prescient tagline, "Git repository hosting: no longer a pain in the ass." I'm not joking here either, look it up. There was, all the way back in …

## In design points

[[designs/p002|P002]]
