---
type: Design Alternative
title: Hidden remote-reference namespace
description: Fetched remote refs are kept under a hidden namespace for maintenance without changing visible refs.
id: '9.19'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p11
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
design_points:
- /designs/p003.md
tags:
- value
- accepted
- client-repository-performance-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Hidden remote-reference namespace

Fetched remote refs are kept under a hidden namespace for maintenance without changing visible refs.

## Evidence

- **s05_p11** (accepts) · [Introducing Scalar](/sources/s5.md) · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …

## In design points

[P003](/designs/p003.md)
