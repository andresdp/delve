---
title: Whole-file local repository caching
type: value
id: '9.10'
status: rejected
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by: []
rejected_by:
- s01_p05
passages: 1
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- rejected
- repository-storage-representation
---

# Whole-file local repository caching

Caches a complete repository file locally to accelerate random access to repository data.

## Evidence

- **s01_p05** (rejects) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
