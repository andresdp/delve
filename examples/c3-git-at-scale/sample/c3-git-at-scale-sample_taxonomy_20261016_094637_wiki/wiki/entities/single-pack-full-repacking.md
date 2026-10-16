---
title: Single-pack full repacking
type: value
id: '12.2'
status: rejected
dimension: '[[concepts/compaction-maintenance-technique|Compaction Maintenance Technique]]'
accepted_by: []
rejected_by:
- s05_p12
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p024|P024]]'
tags:
- value
- rejected
- compaction-maintenance-technique
---

# Single-pack full repacking

Maintenance consolidates all accumulated packfiles into one packfile through a full rewrite.

## Evidence

- **s05_p12** (rejects) · [[sources/s5|Introducing Scalar]] · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …

## In design points

[[designs/p024|P024]]
