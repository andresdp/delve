---
title: Small-pack batch selection
type: value
id: '12.25'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p13
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p007|P007]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Small-pack batch selection

Each incremental repack selects a bounded set of small packfiles.

## Evidence

- **s05_p13** (accepts) · [[sources/s5|Introducing Scalar]] · Clean up pack-files
  > However, there is still a problem. If we let the number of pack-files grow without bound, Git cannot hold file handles to all pack-files at once. Rewriting pack-files could also reduce space costs due to better delta encoding. To solve this problem, Scalar has a pack-file maintenance step which performs an \*incremental\* repack by selecting a batch of small pack-files …

## In design points

[[designs/p007|P007]]
