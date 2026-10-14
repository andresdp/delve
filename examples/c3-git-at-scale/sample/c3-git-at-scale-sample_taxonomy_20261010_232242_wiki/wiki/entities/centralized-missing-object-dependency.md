---
title: Centralized missing-object dependency
type: value
id: '11.8'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s05_p08
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Centralized missing-object dependency

Allow clients to depend on a central service to obtain objects absent from the local repository.

## Evidence

- **s05_p08** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
