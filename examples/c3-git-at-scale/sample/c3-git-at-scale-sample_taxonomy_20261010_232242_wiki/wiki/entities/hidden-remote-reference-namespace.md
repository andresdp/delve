---
title: Hidden remote-reference namespace
type: value
id: '11.6'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s05_p11
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Hidden remote-reference namespace

Fetched references are stored under a hidden Scalar namespace, supplying commit-graph inputs without changing normal remote-tracking references.

## Evidence

- **s05_p11** (accepts) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …
