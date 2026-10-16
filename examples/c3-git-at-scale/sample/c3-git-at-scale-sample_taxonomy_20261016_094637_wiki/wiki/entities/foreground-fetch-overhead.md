---
type: Outcome
title: Foreground-fetch overhead
description: Generating commit-graph data during foreground fetch adds user-visible fetch work.
id: '9.31'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- outcome
- client-repository-performance-strategy
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Foreground-fetch overhead

Generating commit-graph data during foreground fetch adds user-visible fetch work.

## Evidence

- **s05_p11** (supports) · [Introducing Scalar](/sources/s5.md) · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …
