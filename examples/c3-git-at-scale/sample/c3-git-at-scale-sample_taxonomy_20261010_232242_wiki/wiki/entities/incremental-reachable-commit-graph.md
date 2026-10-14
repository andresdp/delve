---
title: Incremental reachable-commit graph
type: value
id: '12.18'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p01
- s05_p11
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p004|P004]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Incremental reachable-commit graph

Split incremental commit-graph files include reachable commits while limiting repeated update cost.

## Evidence

- **s05_p01** (accepts) · [[sources/s5|Introducing Scalar]]
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p11** (accepts) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …

## In design points

[[designs/p004|P004]]
