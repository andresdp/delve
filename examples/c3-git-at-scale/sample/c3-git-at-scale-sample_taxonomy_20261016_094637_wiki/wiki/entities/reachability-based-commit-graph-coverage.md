---
type: Design Alternative
title: Reachability-based commit-graph coverage
description: Background graph generation includes every commit reachable through visible and hidden references.
id: '9.22'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p01
- s05_p11
rejected_by: []
passages: 2
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- accepted
- client-repository-performance-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Reachability-based commit-graph coverage

Background graph generation includes every commit reachable through visible and hidden references.

## Evidence

- **s05_p01** (accepts) · [Introducing Scalar](/sources/s5.md)
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p11** (accepts) · [Introducing Scalar](/sources/s5.md) · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …
