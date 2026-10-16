---
title: Complete object transfer
type: value
id: '6.1'
status: outcome
dimension: '[[concepts/large-repository-object-acquisition|Large-Repository Object Acquisition]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
tags:
- value
- outcome
- large-repository-object-acquisition
---

# Complete object transfer

Transfers and verifies the full repository object graph during a conventional clone, creating substantial network, server, client, and latency costs.

## Evidence

- **s05_p08** (supports) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
