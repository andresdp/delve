---
type: Outcome
title: Complete object transfer
description: Transfers and verifies the full repository object graph during a conventional clone, creating substantial network, server, client, and latency costs.
id: '6.1'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-gvfs.md
tags:
- value
- outcome
- large-repository-object-acquisition
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Complete object transfer

Transfers and verifies the full repository object graph during a conventional clone, creating substantial network, server, client, and latency costs.

## Evidence

- **s05_p08** (supports) · [Introducing Scalar](/sources/s5.md) · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
