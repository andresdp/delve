---
title: Hidden-reference background fetch
type: value
id: '4.12'
status: accepted
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s05_p11
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p019|P019]]'
tags:
- value
- accepted
- client-repository-workload-scaling
---

# Hidden-reference background fetch

Fetch objects and hidden refs asynchronously while preserving visible branch references for explicit foreground updates.

## Evidence

- **s05_p11** (accepts) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …

## In design points

[[designs/p019|P019]]
