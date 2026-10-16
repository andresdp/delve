---
type: Outcome
title: Pack-index scan growth
description: Accumulating separate pack indexes makes object lookup progressively slower.
id: '12.5'
dimension: /concepts/compaction-maintenance-technique.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- outcome
- compaction-maintenance-technique
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Pack-index scan growth

Accumulating separate pack indexes makes object lookup progressively slower.

## Evidence

- **s05_p12** (supports) · [Introducing Scalar](/sources/s5.md) · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …
