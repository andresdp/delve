---
title: Packfile size-minimizing layout
type: value
id: '9.13'
status: accepted
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p05
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- accepted
- repository-storage-representation
---

# Packfile size-minimizing layout

Places Git objects in packfiles using a compact size-minimization heuristic rather than preserving repository-DAG locality.

## Evidence

- **s01_p05** (accepts) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
