---
title: Hidden remote-reference namespace
type: value
id: '9.19'
status: accepted
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s05_p11
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p003|P003]]'
tags:
- value
- accepted
- client-repository-performance-strategy
---

# Hidden remote-reference namespace

Fetched remote refs are kept under a hidden namespace for maintenance without changing visible refs.

## Evidence

- **s05_p11** (accepts) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …

## In design points

[[designs/p003|P003]]
