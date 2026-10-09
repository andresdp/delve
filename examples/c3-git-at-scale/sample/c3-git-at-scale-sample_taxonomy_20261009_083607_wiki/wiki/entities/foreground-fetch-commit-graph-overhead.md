---
title: Foreground-fetch commit-graph overhead
type: value
id: '4.28'
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

# Foreground-fetch commit-graph overhead

Writing commit graphs during foreground fetches adds command latency and motivates asynchronous maintenance.

## Evidence

- **s05_p11** (supports) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …
