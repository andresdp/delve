---
type: Outcome
title: Pack-count and storage reduction
description: Incremental repacking reduces pack-file count, storage footprint, and pack-management pressure.
id: '12.4'
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

# Pack-count and storage reduction

Incremental repacking reduces pack-file count, storage footprint, and pack-management pressure.

## Evidence

- **s05_p13** (supports) · [Introducing Scalar](/sources/s5.md) · Clean up pack-files
  > However, there is still a problem. If we let the number of pack-files grow without bound, Git cannot hold file handles to all pack-files at once. Rewriting pack-files could also reduce space costs due to better delta encoding. To solve this problem, Scalar has a pack-file maintenance step which performs an \*incremental\* repack by selecting a batch of small pack-files …
