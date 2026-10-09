---
title: Central-server on-demand object retrieval
type: value
id: '4.10'
status: accepted
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s05_p08
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
tags:
- value
- accepted
- client-repository-workload-scaling
---

# Central-server on-demand object retrieval

Rely on a central server to supply Git objects missing from the client when commands or working-directory scope require them.

## Evidence

- **s05_p08** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
