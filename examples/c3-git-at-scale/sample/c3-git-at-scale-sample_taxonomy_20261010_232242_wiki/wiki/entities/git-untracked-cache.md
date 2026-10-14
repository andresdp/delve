---
title: Git untracked cache
type: value
id: '12.8'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p05
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Git untracked cache

Cache information about untracked paths to reduce repeated working-directory inspection for repositories with many files.

## Evidence

- **s05_p05** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 1: Focus on the files that matter
  > The most common Git commands are \`git status\` to see what change are available, \`git add\` to stage those changes before committing, and \`git checkout\` to change your working directory to match a different version. We call these the \*core commands\*. Each core command inspects the working directory to see how Git’s view of the working directory agrees with what …
