---
title: Pack-index scan growth
type: value
id: '12.5'
status: outcome
dimension: '[[concepts/compaction-maintenance-technique|Compaction Maintenance Technique]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- compaction-maintenance-technique
---

# Pack-index scan growth

Accumulating separate pack indexes makes object lookup progressively slower.

## Evidence

- **s05_p12** (supports) · [[sources/s5|Introducing Scalar]] · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …
