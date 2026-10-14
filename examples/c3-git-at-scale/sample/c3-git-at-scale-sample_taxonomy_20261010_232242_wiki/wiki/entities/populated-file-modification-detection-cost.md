---
title: Populated-file modification detection cost
type: value
id: '12.36'
status: outcome
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by: []
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- client-repository-and-working-tree-scaling
---

# Populated-file modification detection cost

Detecting modifications among populated working-directory files imposes additional client-side processing cost.

## Evidence

- **s05_p06** (supports) · [[sources/s5|Introducing Scalar]] · Populated size
  > How many paths in the index are actually in your working directory? This is normally equal to the number of tracked files in the index, but Git’s sparse-checkout feature can make it smaller. It takes a little bit of work to design your repository to work with sparse-checkout, but it can allow most developers to populate a fraction of the …
- **s05_p07** (supports) · [[sources/s5|Introducing Scalar]] · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
