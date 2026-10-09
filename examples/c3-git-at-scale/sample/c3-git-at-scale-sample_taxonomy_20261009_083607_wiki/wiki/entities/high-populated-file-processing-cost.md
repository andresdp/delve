---
title: High populated-file processing cost
type: value
id: '4.31'
status: outcome
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- client-repository-workload-scaling
---

# High populated-file processing cost

Populating and detecting modifications in working-tree files imposes substantial data movement and processing cost.

## Evidence

- **s05_p06** (supports) · [[sources/s5|Introducing Scalar]] · Populated size
  > How many paths in the index are actually in your working directory? This is normally equal to the number of tracked files in the index, but Git’s sparse-checkout feature can make it smaller. It takes a little bit of work to design your repository to work with sparse-checkout, but it can allow most developers to populate a fraction of the …
