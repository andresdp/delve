---
type: Design Alternative
title: Loose-object cleanup
description: Maintenance removes accumulated loose-object storage to reduce disk and lookup overhead.
id: '12.3'
dimension: /concepts/compaction-maintenance-technique.md
accepted_by:
- s05_p12
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
design_points:
- /designs/p007.md
- /designs/p008.md
- /designs/p010.md
- /designs/p020.md
tags:
- value
- accepted
- compaction-maintenance-technique
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Loose-object cleanup

Maintenance removes accumulated loose-object storage to reduce disk and lookup overhead.

## Evidence

- **s05_p12** (accepts) · [Introducing Scalar](/sources/s5.md) · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …

## In design points

[P007](/designs/p007.md), [P008](/designs/p008.md), [P010](/designs/p010.md), [P020](/designs/p020.md)
