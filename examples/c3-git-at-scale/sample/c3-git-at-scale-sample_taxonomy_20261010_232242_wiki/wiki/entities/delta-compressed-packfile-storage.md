---
title: Delta-compressed packfile storage
type: value
id: '9.11'
status: accepted
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p05
- s05_p12
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p001|P001]]'
tags:
- value
- accepted
- repository-storage-representation
---

# Delta-compressed packfile storage

Stores most packfile objects as deltas to reduce storage size at the cost of additional read hops.

## Evidence

- **s01_p05** (accepts) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
- **s05_p12** (accepts) · [[sources/s5|Introducing Scalar]] · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …

## In design points

[[designs/p001|P001]]
