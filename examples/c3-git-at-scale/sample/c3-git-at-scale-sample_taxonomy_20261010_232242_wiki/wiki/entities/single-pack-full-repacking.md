---
title: Single-pack full repacking
type: value
id: '12.31'
status: rejected
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by: []
rejected_by:
- s05_p12
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p015|P015]]'
tags:
- value
- rejected
- client-repository-and-working-tree-scaling
---

# Single-pack full repacking

Rewriting all repository objects into one consolidated pack-file during maintenance.

## Evidence

- **s05_p12** (rejects) · [[sources/s5|Introducing Scalar]] · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …

## In design points

[[designs/p015|P015]]
