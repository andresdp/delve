---
title: Improved delta-encoding efficiency
type: value
id: '12.40'
status: outcome
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- client-repository-and-working-tree-scaling
---

# Improved delta-encoding efficiency

Pack rewriting can improve delta encoding and reduce repository storage.

## Evidence

- **s05_p13** (supports) · [[sources/s5|Introducing Scalar]] · Clean up pack-files
  > However, there is still a problem. If we let the number of pack-files grow without bound, Git cannot hold file handles to all pack-files at once. Rewriting pack-files could also reduce space costs due to better delta encoding. To solve this problem, Scalar has a pack-file maintenance step which performs an \*incremental\* repack by selecting a batch of small pack-files …
