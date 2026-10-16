---
title: Pack-count and storage reduction
type: value
id: '12.4'
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

# Pack-count and storage reduction

Incremental repacking reduces pack-file count, storage footprint, and pack-management pressure.

## Evidence

- **s05_p13** (supports) · [[sources/s5|Introducing Scalar]] · Clean up pack-files
  > However, there is still a problem. If we let the number of pack-files grow without bound, Git cannot hold file handles to all pack-files at once. Rewriting pack-files could also reduce space costs due to better delta encoding. To solve this problem, Scalar has a pack-file maintenance step which performs an \*incremental\* repack by selecting a batch of small pack-files …
