---
title: Reduced initial clone footprint
type: value
id: '12.33'
status: outcome
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
tags:
- value
- outcome
- client-repository-and-working-tree-scaling
---

# Reduced initial clone footprint

Filtered object transfer substantially reduces the client download compared with transferring complete repository history.

## Evidence

- **s05_p08** (supports) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
