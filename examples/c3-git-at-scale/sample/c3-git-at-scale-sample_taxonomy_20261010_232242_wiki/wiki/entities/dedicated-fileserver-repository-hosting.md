---
title: Dedicated fileserver repository hosting
type: value
id: '9.9'
status: mixed
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p05
rejected_by:
- s01_p02
passages: 2
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- mixed
- repository-storage-representation
---

# Dedicated fileserver repository hosting

Keeps repositories on dedicated fileservers and exposes repository operations through remote procedure calls.

## Evidence

- **s01_p02** (rejects) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p05** (accepts) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
