---
type: Design Alternative
title: Single-pack full repacking
description: Maintenance consolidates all accumulated packfiles into one packfile through a full rewrite.
id: '12.2'
dimension: /concepts/compaction-maintenance-technique.md
accepted_by: []
rejected_by:
- s05_p12
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
design_points:
- /designs/p024.md
tags:
- value
- rejected
- compaction-maintenance-technique
stance: rejected
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Single-pack full repacking

Maintenance consolidates all accumulated packfiles into one packfile through a full rewrite.

## Evidence

- **s05_p12** (rejects) · [Introducing Scalar](/sources/s5.md) · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …

## In design points

[P024](/designs/p024.md)
